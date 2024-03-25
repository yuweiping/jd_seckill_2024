
### 更新说明：
1. 移除了多进程，work_count参数作废
2. 移除了计算本地时间和jd的差值，如果本地时间和JD差别较大，需自己手动调整本机时间。
3. ~~使用allow_redirects=True优化了转跳请求的写法，目前看对请求时间没影响~~,有问题回退了
4. 将gen_token,js_tk 调整到了抢购之前的2s，所以maotai的抢购时间buy_time建议写成 12:00:00
5. 增加了requests session的连接池设置
6. get_seckill_action_url增加了次数限制，避免一直失败后无法退出
----
多线程目前看会阻塞网络，效果也不好，方案还在尝试中。


