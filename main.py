# -*- coding: utf-8 -*-
# 京东预约脚本

import time
from datetime import datetime, timedelta

import schedule
from jd_logger import logger
from jd_seckill import JdSeckill
from config import global_config

import os
import math

proxy = global_config.getRaw('config', 'proxies')
if proxy:
    logger.info('已配置系统代理：'+proxy)
os.environ["http_proxy"] = proxy
os.environ["https_proxy"] = proxy


def task_time(time_str, sec):
    time_format = '%H:%M:%S'
    time_object = datetime.strptime(time_str, time_format)
    return datetime.strftime(time_object + timedelta(seconds=-sec), time_format)


if __name__ == '__main__':
    jdSeckill = JdSeckill()
    cha = jdSeckill.jd_local_time_diff()
    # jd时间比本机快，job启动时间就要比预定时间要早
    cha_time = math.ceil(cha / 1000.0)
    if cha_time >= 1:
        logger.warning("jd时间比本机快，job启动时间就要比预定时间要早" + str(cha_time) + "S")
    else:
        cha_time = 0
    if jdSeckill.address is None:
        jdSeckill.get_address_by_pin()

    task_list = eval(global_config.getRaw('config', 'task'))
    logger.info('启动后自动执行预约...')
    for task in task_list:
        jdSeckill.make_reserve(task)
        logger.info(
            '创建定时任务:%s, %s进行预约, %s准备抢购。' % (task['name'], task['make_reserve_time'], task_time(task['buy_time'], cha_time)))
        schedule.every().day.at(task['make_reserve_time']).do(jdSeckill.make_reserve, task)
        schedule.every().day.at(task_time(task['buy_time'], cha_time)).do(jdSeckill.seckill_by_proc_pool, task)

    while True:
        schedule.run_pending()
        time.sleep(1)
