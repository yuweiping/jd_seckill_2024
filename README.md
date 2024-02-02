茅台现在不好抢了，但是抢mate60还是很容易的。同样适用于JD的其他抢购商品。

1. 将config-test.ini改名为config.ini
2. 按照使用手册抓包补全信息，注意config中的配置信息是不用加引号的，**末尾不要有分号**。
3. main.py

如果sign失败大概率是api_jd_url有问题，大家可参考如下格式
api_jd_url = https://api.m.jd.com/client.action?functionId=genToken&clientVersion=12.2.2……

---

**注意本库只能作为学习用途, 造成的任何问题与本库开发者无关, 如侵犯到你的权益，请联系删除**

sign部分使用的是如下大佬的库，有兴趣的可以关注下

[n1ptune/jdSign: JD signature algorithm implemented by python (github.com)](https://github.com/n1ptune/jdSign)

据说抢茅台需要plus分>103 ,本程序是否会造成封号，降分未完全测试，**后果自负**。

目前我只用自己的账号测试过好用。暂不支持鸿蒙和IOS。如果sign失败，一般是配置文件有问题，也可以尝试换其他抓包软件。

如果各位老板需要联系我支持，请**打赏后再加微信**（小号s84iis）并注明已捐赠。

<img src=".\doc\wx_code.png" alt="wx" style="zoom:40%;" />

