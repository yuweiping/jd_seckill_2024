import os

import util
from config import global_config
from jd_logger import logger
from jd_seckill import JdSeckill

proxy = global_config.getRaw('config', 'proxies')
if proxy:
    logger.info('已配置系统代理：' + proxy)
os.environ["http_proxy"] = proxy
os.environ["https_proxy"] = proxy

if __name__ == "__main__":
    address_list = JdSeckill().get_address_list()
    for address in address_list:
        addressId = str(address['Id'])
        where = util.decrypt(address['Where'])
        default = address['addressDefault']
        message = f"id {addressId}  {where}  "+("" if not default else "---默认地址--- ")
        logger.info(message)
