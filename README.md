
### 更新说明：
1. 移除了多进程，work_count参数作废
2. 移除了计算本地时间和jd的差值，如果本地时间和JD差别较大，需自己手动调整本机时间。
3. ~~使用allow_redirects=True优化了转跳请求的写法，目前看对请求时间没影响~~,有问题回退了
4. 将gen_token,js_tk 调整到了抢购之前的2s，因为schedule不能精确到毫秒，所以最好还是将抢购时间提前1s
5. 增加了requests session的连接池设置
6. get_seckill_action_url增加了次数限制，避免一直失败后无法退出
7. 移除了jd_url的oaid必填校验
8. 添加了版本号自动管理setuptools_scm
----
多线程目前看会阻塞网络，效果也不好，方案还在尝试中。


