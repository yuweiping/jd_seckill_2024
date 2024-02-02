import json
import multiprocessing
import os
import time
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timedelta

from SpiderSession import SpiderSession
from config import global_config
from jd_logger import logger
import util
from urllib import parse


class JdSeckill(object):

    def __init__(self):
        self.has_gen_seckill_url = False
        self.cha = 0
        self.order_data = None
        self.seckill_action_url = ''
        self.address = None
        self.spider_session = SpiderSession()
        self.session = self.spider_session.get_session()
        self.sku_id = ''
        self.buy_time = ''
        self.seckill_num = 1
        self.jsTk_info = None
        self.has_gen_order = False
        self.fp = global_config.getRaw('config', 'fp')
        self.push_token = global_config.getRaw('config', 'push_token')

    def make_reserve(self, task):
        """商品预约"""
        functionId = "appoint"
        body = {"autoAddCart": "0", "bsid": "", "check": "0", "ctext": "", "isShowCode": "0", "mad": "0",
                "skuId": task['sku_id'],
                "type": "1"}
        data = 'body=' + json.dumps(body, separators=(',', ':')) + '&'
        resp = self.spider_session.requestWithSign(functionId, body, data)
        resp_json = resp.json()

        try:
            if resp_json['title'] == '您已成功预约，无需重复预约' or resp_json['title'] == '预约成功！':
                logger.info(task['name'] + resp_json['title'])
            else:
                logger.error(task['name'] + ' 预约失败:' + resp_json['content'])
        except Exception as e:
            logger.error(task['name'] + ' 预约失败:' + str(e))

    def jd_time(self):
        """
        从京东服务器获取时间戳
        :return:
        """
        start_time = util.local_time()
        url = 'https://api.m.jd.com'
        resp = self.spider_session.get(url)
        jd_timestamp = int(resp.headers.get('X-API-Request-Id')[-13:])
        end_time = util.local_time()
        req_time = end_time - start_time
        logger.info('单次请求时间' + str(req_time) + ' ms')
        if req_time > 800:
            if os.environ["http_proxy"]:
                logger.warn('单次请求时间过长很难抢到，请更换代理')
            else:
                logger.warn('单次请求时间过长很难抢到，请检查网络')
        return jd_timestamp

    def jd_local_time_diff(self):
        """
        计算京东服务器与本地时间差
        """
        jd_time = self.jd_time()
        local_time = util.local_time()
        self.cha = jd_time - local_time
        logger.info('服务器时间: ' + util.format_time(jd_time, '%Y-%m-%d %H:%M:%S.%f'))
        logger.info('本机时间:   ' + util.format_time(local_time, '%Y-%m-%d %H:%M:%S.%f'))
        logger.info('JD服务器与本机时间差值为：' + str(self.cha) + ' ms')
        if abs(self.cha / 1000.0) >= 5:
            logger.warning('时间差值过大，建议先同步下时间再重启下软件')
        return self.cha

    def seckill_by_proc_pool(self, task):
        # 重置cookie
        self.reset_cookies()
        self.sku_id = task['sku_id']
        self.buy_time = task['buy_time'] + '.000'

        seckill_stop_event = multiprocessing.Manager().Event()
        # 增加进程配置
        work_count = int(global_config.getRaw('config', 'work_count'))
        with ProcessPoolExecutor(work_count) as pool:
            for i in range(work_count):
                pool.submit(self.seckill, seckill_stop_event)

    def seckill(self, seckill_stop_event):
        while not seckill_stop_event.is_set():
            try:
                # 先获取seckill.action
                if not self.has_gen_seckill_url:
                    self.get_seckill_action_url()
                    self.request_seckill_url()
                    self._do_jsTk(self.seckill_action_url)
            except Exception as e:
                self.has_gen_seckill_url = False
                logger.error('seckill_url生成异常' + str(e))

            try:
                # 生成订单信息
                if not self.has_gen_order:
                    self._get_init_info()
                    self.gen_order_data()
            except Exception as e:
                self.has_gen_order = False
                logger.error('订单生成异常' + str(e))
            try:
                # 提交订单
                if self.has_gen_order:
                    self.update_seckill_cookie()
                    self.submit_order(seckill_stop_event)
            except Exception as e:
                logger.error('抢购发生异常' + str(e))
                # 抛异常时，只停止自己的进程
                break
            # 判断是否停止
            self.seckill_canstill_running(seckill_stop_event)

    def update_seckill_cookie(self):
        cookie_str = '3AB9D23F7A4B3CSS=' + self.jsTk_info['token']
        cookie_str += ';3AB9D23F7A4B3C9B=' + self.jsTk_info['eid']
        cookie_str += ';_gia_d=' + str(self.jsTk_info['gia_d'])
        cookie_str += ';__jd_ref_cls=MSecKillBalance_Order_Submit'
        # logger.info('update cookie: ' + cookie_str)
        self.spider_session.update_cookies(cookie_str)

    def reset_cookies(self):
        self.session.cookies = self.spider_session.init_cookies()

    def seckill_canstill_running(self, seckill_stop_event):
        """
        计算开始时间
        :return:
        """
        time_format = '%H:%M:%S.%f'
        time_object = datetime.strptime(self.buy_time, time_format)
        end_time_str = datetime.strftime(
            time_object + timedelta(seconds=int(global_config.getRaw('config', 'continue_time'))), time_format)
        end_time = util.str2timestamp(end_time_str)
        # jd 服务器当前时间
        current_time = util.local_time() + self.cha
        if current_time > end_time:
            seckill_stop_event.set()
            logger.info('超过允许的运行时间，任务结束。')

    def request_seckill_url(self):
        logger.info('3. seckill.action ')
        resp = self.spider_session.get(url=self.seckill_action_url, allow_redirects=False)
        set_cookie = resp.headers.get('Set-Cookie')
        if set_cookie:
            self.spider_session.update_cookies(set_cookie)
        else:
            raise Exception('seckill.action访问失败')

    def submit_order(self, seckill_stop_event):
        url = 'https://marathon.jd.com/seckillnew/orderService/submitOrder.action?skuId=%s' % self.sku_id

        logger.info('7. submitOrder.action...')
        # 修改设置请求头的方式
        self.session.headers['x-rp-client'] = 'h5_1.0.0'
        self.session.headers['x-referer-page'] = 'https://marathon.jd.com/seckillM/seckill.action'
        self.session.headers['origin'] = 'https://marathon.jd.com'
        self.session.headers['Referer'] = self.seckill_action_url
        resp = self.spider_session.post(
            url=url,
            data=self.order_data,
            allow_redirects=False)
        # logger.info(resp.text)
        try:
            # 解析json
            resp_json = resp.json()
            # 返回信息
            # 抢购失败：
            # {'errorMessage': '很遗憾没有抢到，再接再厉哦。', 'orderId': 0, 'resultCode': 60074, 'skuId': 0, 'success': False}
            # {'errorMessage': '抱歉，您提交过快，请稍后再提交订单！', 'orderId': 0, 'resultCode': 60017, 'skuId': 0, 'success': False}
            # {'errorMessage': '系统正在开小差，请重试~~', 'orderId': 0, 'resultCode': 90013, 'skuId': 0, 'success': False}
            # 抢购成功：
            # {"appUrl":"xxxxx","orderId":820227xxxxx,"pcUrl":"xxxxx","resultCode":0,"skuId":0,"success":true,"totalMoney":"xxxxx"}
            if resp_json.get('success'):
                order_id = resp_json.get('orderId')
                logger.info('抢购成功，订单号------------------->' + str(order_id))
                self.send_msg('抢购成功', '抢购成功，订单号:' + str(order_id))
                seckill_stop_event.set()
            else:
                logger.error('抢购失败，返回信息:{}'.format(resp_json))
        except Exception as e:
            raise Exception('抢购失败，猜测已经抢完了，停止进程...' + str(e))

    def get_seckill_action_url(self):
        url = self.gen_token()
        while True:
            self.jump_url(url)
            if self.seckill_action_url != '':
                logger.info("get_seckill_action_url成功...")
                break
            else:
                logger.info("get_seckill_action_url失败，自动重试...")

    def gen_token(self):
        logger.info("1. genToken...")
        functionId = 'genToken'
        body = {"action": "to", 'to': parse.quote_plus('https://divide.jd.com/user_routing?skuId=' + self.sku_id)}
        # 抓包的body
        data = 'body=' + parse.quote_plus(json.dumps(body, separators=(',', ':'))) + '&'
        resp = self.spider_session.requestWithSign(functionId, body, data)
        appjmp_url = ''
        if util.response_status(resp):
            token_params = resp.json()
            if token_params['code'] == '0':
                appjmp_url = '%s?tokenKey=%s&to=https://divide.jd.com/user_routing?skuId=%s&from=app' % (
                    token_params['url'], token_params['tokenKey'], self.sku_id)
        logger.info('genToken 成功: ' + appjmp_url)
        return appjmp_url

    def jump_url(self, url):
        # https://un.m.jd.com/cgi-bin/app/appjmp
        # https://divide.jd.com/user_routing?skuId=100012043978&mid=nyPX0yoIQBnq1Tv__rBL6pnsn8OGYGhzjXbNhTsir4A&sid=
        self.seckill_action_url = url
        code = 302
        while code == 302 and self.seckill_action_url != '':
            # logger.info("2. jump_url: " + self.seckill_action_url)
            resp = self.spider_session.get(url=self.seckill_action_url, allow_redirects=False)
            code = resp.status_code
            if code == 302:
                self.seckill_action_url = resp.headers.get('location')
            if self.seckill_action_url != 'https://marathon.jd.com/mobile/koFail.html':
                set_cookie = resp.headers.get('Set-Cookie')
                if set_cookie:
                    self.spider_session.update_cookies(set_cookie)
            else:
                self.seckill_action_url = ''
        # print(self.seckill_action_url)
        if not self.seckill_action_url.startswith('https://marathon.jd.com/seckillM/seckill.action'):
            logger.info(self.seckill_action_url)
            self.seckill_action_url = ''

    def gen_order_data(self):
        logger.info('6. gen_order_data...')
        default_address = self.init_info['address']  # 默认地址dict
        invoice_info = self.init_info['invoiceInfo']  # 默认发票信息dict, 有可能不返回
        token = self.init_info['token']
        data = {
            'num': self.init_info['seckillSkuVO']['num'],
            'addressId': default_address['id'],
            'name': default_address['name'],
            'provinceId': default_address['provinceId'],
            'provinceName': default_address['provinceName'],
            'cityId': default_address['cityId'],
            'cityName': default_address['cityName'],
            'countyId': default_address['countyId'],
            'countyName': default_address['countyName'],
            'townId': default_address['townId'],
            'townName': default_address['townName'],
            'addressDetail': default_address['addressDetail'],
            'mobile': default_address['mobile'],
            'mobileKey': default_address['mobileKey'],
            'email': '',
            'invoiceTitle': invoice_info['invoiceTitle'],
            'invoiceContent': invoice_info['invoiceContentType'],
            'invoicePhone': invoice_info['invoicePhone'],
            'invoicePhoneKey': invoice_info['invoicePhoneKey'],
            'invoice': True,
            'password': '',
            'codTimeType': '3',
            'paymentType': '4',
            'overseas': '0',
            'phone': '',
            'areaCode': default_address['areaCode'],
            'token': token,
            'skuId': self.sku_id,
            'eid': self.jsTk_info['token']
        }
        self.has_gen_order = True
        self.order_data = data

    def _get_init_info(self):
        """获取秒杀初始化信息（包括：地址，发票，token）
        :return: 初始化信息组成的dict
        """
        logger.info('4. init.action...')
        url = 'https://marathon.jd.com/seckillnew/orderService/init.action'
        payload = {
            'sku': self.sku_id,
            'num': self.seckill_num,
            'deliveryMode': '',
            'id': self.address['Id'],
            'provinceId': self.address['Province'],
            'cityId': self.address['IdCity'],
            'countyId': self.address['IdArea'],
            'townId': self.address['IdTown'],
        }
        resp = self.spider_session.post(url=url, data=payload)
        # logger.info('生成订单信息：' + str(resp))
        try:
            if resp.json()['address']:
                self.init_info = resp.json()
        except Exception as e:
            raise Exception('init.action失败,自动重试...')

    # init之后获取新的eid
    def _do_jsTk(self, seckill_url):
        logger.info('jsTk.do... ' + seckill_url)
        url = 'https://gia.jd.com/jsTk.do?'
        g = {"pin": "", "oid": "", "bizId": "JD_INDEP", "mode": "strict", "p": "s",
             "fp": self.fp, "ctype": 1, "v": "3.1.1.0", "f": "3",
             "o": "marathon.jd.com/seckillM/seckill.action",
             "qs": "skuId=100012043978&num=1&rid=1701403262&deliveryMode=#/", "qi": ""}
        tmp_url = parse.urlparse(seckill_url)
        query = tmp_url.query
        g['qs'] = query + '#/'
        a = util.TDEncrypt(g)
        url = url + 'a=' + parse.quote(a, safe='*,/')
        d = {"ts": {"deviceTime": 1701403263780, "deviceEndTime": 1701403263780},
             "ca": {"tdHash": "e7d49789d9eb24d0cd049db271f941f", "contextName": "webgl,experimental-webgl",
                    "webglversion": "WebGL 1.0 (OpenGL ES 2.0 Chromium)",
                    "shadingLV": "WebGL GLSL ES 1.0 (OpenGL ES GLSL ES 1.0 Chromium)", "vendor": "WebKit",
                    "renderer": "WebKit WebGL",
                    "extensions": ["ANGLE_instanced_arrays", "EXT_blend_minmax", "EXT_color_buffer_half_float",
                                   "EXT_float_blend", "EXT_texture_filter_anisotropic",
                                   "WEBKIT_EXT_texture_filter_anisotropic", "EXT_sRGB", "OES_element_index_uint",
                                   "OES_fbo_render_mipmap", "OES_standard_derivatives", "OES_texture_float",
                                   "OES_texture_float_linear", "OES_texture_half_float",
                                   "OES_texture_half_float_linear", "OES_vertex_array_object",
                                   "WEBGL_color_buffer_float", "WEBGL_compressed_texture_astc",
                                   "WEBGL_compressed_texture_etc", "WEBGL_compressed_texture_etc1",
                                   "WEBGL_debug_renderer_info", "WEBGL_debug_shaders", "WEBGL_depth_texture",
                                   "WEBKIT_WEBGL_depth_texture", "WEBGL_lose_context", "WEBKIT_WEBGL_lose_context",
                                   "WEBGL_multi_draw"], "wuv": "Qualcomm", "wur": "Adreno (TM) 730"},
             "m": {"compatMode": "CSS1Compat"}, "fo": ["Bauhaus 93", "Casual"],
             "n": {"vendorSub": "", "productSub": "20030107", "vendor": "Google Inc.", "maxTouchPoints": 5,
                   "hardwareConcurrency": 8, "cookieEnabled": True, "appCodeName": "Mozilla", "appName": "Netscape",
                   "appVersion": "", "platform": "Linux aarch64", "product": "Gecko", "userAgent": "",
                   "language": "zh-CN", "onLine": True, "webdriver": False, "javaEnabled": False, "deviceMemory": 8,
                   "enumerationOrder": ["vendorSub", "productSub", "vendor", "maxTouchPoints", "userActivation",
                                        "doNotTrack", "geolocation", "connection", "plugins", "mimeTypes",
                                        "webkitTemporaryStorage", "webkitPersistentStorage", "hardwareConcurrency",
                                        "cookieEnabled", "appCodeName", "appName", "appVersion", "platform", "product",
                                        "userAgent", "language", "languages", "onLine", "webdriver", "getBattery",
                                        "getGamepads", "javaEnabled", "sendBeacon", "vibrate", "scheduling",
                                        "mediaCapabilities", "locks", "wakeLock", "usb", "clipboard", "credentials",
                                        "keyboard", "mediaDevices", "storage", "serviceWorker", "deviceMemory",
                                        "bluetooth", "getUserMedia", "requestMIDIAccess", "requestMediaKeySystemAccess",
                                        "webkitGetUserMedia", "clearAppBadge", "setAppBadge"]}, "p": [],
             "w": {"devicePixelRatio": 3, "screenTop": 0, "screenLeft": 0},
             "s": {"availHeight": 904, "availWidth": 407, "colorDepth": 24, "height": 904, "width": 407,
                   "pixelDepth": 24},
             "sc": {"ActiveBorder": "rgb(255, 255, 255)", "ActiveCaption": "rgb(204, 204, 204)",
                    "AppWorkspace": "rgb(255, 255, 255)", "Background": "rgb(99, 99, 206)",
                    "ButtonFace": "rgb(221, 221, 221)", "ButtonHighlight": "rgb(221, 221, 221)",
                    "ButtonShadow": "rgb(136, 136, 136)", "ButtonText": "rgb(0, 0, 0)", "CaptionText": "rgb(0, 0, 0)",
                    "GrayText": "rgb(128, 128, 128)", "Highlight": "rgb(181, 213, 255)",
                    "HighlightText": "rgb(0, 0, 0)", "InactiveBorder": "rgb(255, 255, 255)",
                    "InactiveCaption": "rgb(255, 255, 255)", "InactiveCaptionText": "rgb(127, 127, 127)",
                    "InfoBackground": "rgb(251, 252, 197)", "InfoText": "rgb(0, 0, 0)", "Menu": "rgb(247, 247, 247)",
                    "MenuText": "rgb(0, 0, 0)", "Scrollbar": "rgb(255, 255, 255)",
                    "ThreeDDarkShadow": "rgb(102, 102, 102)", "ThreeDFace": "rgb(192, 192, 192)",
                    "ThreeDHighlight": "rgb(221, 221, 221)", "ThreeDLightShadow": "rgb(192, 192, 192)",
                    "ThreeDShadow": "rgb(136, 136, 136)", "Window": "rgb(255, 255, 255)",
                    "WindowFrame": "rgb(204, 204, 204)", "WindowText": "rgb(0, 0, 0)"},
             "ss": {"cookie": True, "localStorage": True, "sessionStorage": True, "globalStorage": False,
                    "indexedDB": True}, "tz": -480, "lil": "", "wil": ""}
        t = int(time.time())
        d["ts"]["deviceTime"] = t
        d["ts"]["deviceEndTime"] = t + 77
        d["n"]["appVersion"] = self.spider_session.client_version
        d["n"]["userAgent"] = self.spider_session.user_agent
        data = 'd=' + util.TDEncrypt(json.dumps(d, separators=(',', ':')))
        resp = self.spider_session.post(url=url, data=data)
        # logger.info('jsTk.do: ' + str(resp.text))

        try:
            self.jsTk_info = resp.json()['data']
            self.has_gen_seckill_url = True
        except Exception as e:
            logger.error('jsTk.do失败' + str(e))
            raise Exception('jsTk.do失败')

    def get_address_by_pin(self):
        logger.info("get_address...")
        functionId = 'getAddressByPin'
        body = {"isNeedPickAddressList": True, "isOneOrderMultipleAddress": False, "latitudeString": "wAgx7PWl/2s=",
                "layerFlag": False, "longitudeString": "wAgx7PWl/2s=", "pageId": 0, "requestSourceType": 2,
                "selectedPresentAddressId": 0, "settlementVersionCode": 2440, "sourceType": 2,
                "supportNewParamEncode": True}

        # 抓包的body
        data = 'body=' + parse.quote_plus(json.dumps(body, separators=(',', ':'))) + '&'
        resp = self.spider_session.requestWithSign(functionId, body, data)
        resp_json = resp.json()
        if resp_json['code'] != '0':
            raise Exception(str(resp_json))
        address_list = resp_json['addressList']
        for address in address_list:
            if address['addressDefault']:
                self.address = address
                logger.info('获取默认收货地址成功，id：' + str(address['Id']))
        if address is None:
            logger.error('没有设置默认收货地址！！！')

    # 消息推送
    def send_msg(self, title, content):
        if self.push_token == '':
            return
        url = 'http://www.pushplus.plus/send'
        r = self.spider_session.get(url, params={'token': self.push_token,
                                                 'title': title,
                                                 'content': content})
        logger.info(f'通知推送结果：{r.status_code, r.text}')
