# hedwig

hedwig (海德薇, 哈利波特的猫头鹰) 一个用来进行邮件发送队列的工具.

分为 `mailman` 和 `postoffice` 两部分组成.

## mailman

`mailman` 为宿主机邮件发送的服务, 监听本地 25 端口. `msmtp` 发送到 `mailman`. `mailman` 收到后发送  **http** 请求到 `postoffice` 完成第一部分投递

## postoffice

`postoffice` 为邮件发送服务器, 接收到来自 `mailman` 发送的邮件后, `postoffice` 提送邮件到 **MQ** 系统, 由对接 **MQ** 系统的 `worker` 查询收件人地址后直接进行投递, 完成邮件发送

## 投递流程

如查看乱位, 请复制 `README.md` 内容到文本编辑器进行查看


```
                               +                                               +-----------------+
                               |                                               |                 |
+--------------------+         |         +-------------------+           +-----+                 |
| +----------------+ |         |         |                   |           |     |         126.com |
| |                | |         |         | +---------------+ |           |     +-----------------+
| |                +------------------------>              | |           |
| |                | |  http   |         | |               +-------------+
| |         mailman| |         |         | |    postoffice | |           |     +-----------------+
| +--------^-------+ |         |         | +---------------+ |           |     |                 |
|          |         |         |         |         |         |           +-----+                 |
|          |         |         |         |         |         |           |     |         163.com |
|          |         |         |         |  +-------------+  |           |     +-----------------+
|          |         |         |         |  |          MQ |  |           |
|          |         |         |         |  +-------------+  |           |
|          |         |         |         |         |         |           |     +-----------------+
|          |         |         |         | +---------------+ |           |     |                 |
|          |         |         |         | |       worker1 | |           |     |                 |
|          |         |         |         | +---------------+ |           +-----+       gmail.com |
|          |         |         |         | |       worker2 | |           |     +-----------------+
| +----------------+ |         |         | +---------------+ |           |
| |        +       | |         |         | |       worker3 | |           |
| |      msmtp     | |         |         | +---------------+ |           |     +-----------------+
| |             CF | |         |         | |     worker... | |           |     |                 |
| +----------------+ |         |         | +---------------+ |           |     |                 |
|                    |         |         |                   |           +-----+            ...  |
| less.nankai.edu.cn |         |         |    robot.genee.cn |                 +-----------------+
+--------------------+         |         +-------------------+
                               |
                               |
                               +
```

## 部署文档

### mailman

#### 安装依赖

* docker
* docker-compose (依赖 python, python-pip)
* msmtp

#### 部署步骤

1. 首先, 需要确定宿主机 `docker0` 网卡地址为 **172.17.42.1** 还是 **172.17.0.1** (通常情况下 `docker version` 为 1.6.0 以前的, 为 **172.17.42.1**, 之后的为 **172.17.0.1**)

2. 明确欲发送邮件的容器或者宿主机是否安装了 `msmtp`。 安装方法: `sudo apt-get install msmtp`

3. 与发送邮件的容器或者宿主机中 `/etc/msmtprc` 中增加如下配置, 需要注意, `host` 为上述 **步骤 1** 中明确的网卡地址

	```
	defaults
	syslog LOG_MAIL
	account default
	host 172.17.0.1
	from sender@robot.genee.cn
	```

4. 在宿主机中, 进入该项目的 `src/mailman`. 修改 `docker-compose.yml` 配置中的 `172.17.0.1:25:25` 中的 IP 地址为 **步骤 1** 中明确的网卡地址

5. 在部署  `postoffice` 中的服务器中执行 `src/postoffice/key_generator.py` 并根据提示, 生成当前服务器 `fqdn` 对应的配置内容, 按照要求, 填写结果到当前宿主机的 `src/mailman/config.yml` 中

6. 执行 `docker-compose up -d` 进行 `mailman` 部署

### postoffice (worker)

#### 安装依赖

* docker
* docker-compose (依赖 python, python-pip)

#### 部署步骤

1. 在宿主机中, 进入该项目的 `src/postoffice` 中, 在 `config.yml` 中的填写各个节点的配置信息后保存

2. 执行 `docker-compose up -d` 进行 `postoffice` 部署

#### 部署注意事项

1. 使用 `docker-compose up -d` 会自动部署 `beanstalkd` 服务
2. `postoffice` 服务对应的配置文件为 `postoffice.config.yml`
3. `worker` 服务对应的配置文件为 `worker.config.yml`

## HTTP 协议接口 (postoffice http 接口)

`postoffice` 只提供了一个用于发送邮件的接口, 假设部署 `postoffice` 的服务器域名为 **robot.genee.cn**, 如下:

`http://robot.genee.cn/` 为接口地址.

### 参数列表:

* `fqdn`, 为请求发送邮件的服务器的 **FQDN**
* `key`, 为随机字符串, 用于双方进行安全验证
* `email` 为 json 结构字符串, 包含如下内容:
	* mailfrom
	* rcpttos
	* data

* `email` 中 `mailfrom` 为邮件发送方的地址 (配置在 `mailman` 服务器 `/etc/msmtprc` 中, 例如: `sender@robot.genee.cn`

* `email` 中 `rcpttos` 为收件人地址合集, 例如:  `["stenote@163.com"]`
* `email` 中 `data` 为发送邮件的内容(包含, `From:`, `To:`,  `Subject:` 和邮件正文, 例如:

	```
	From: sender@robot.genee.cn
	To: stenote@163.com
	Subject: Hello World

	Hello Stenote
	```

### 返回结果

#### 正常发送邮件

返回 `http` 状态为 **200**

#### 验证失败

返回 `http` 状态为 **401**

## 注意事项

* 邮件发送中, `mailfrom` 需要与 `data` 中的 `From` 需一致, 否则会出现代发的情况产生.
* postoffice 如果发送失败, 请开启 **debug** 模式, 查看邮件发送返回的结果:
    * [163 退信查询](http://help.163.com/09/1224/17/5RAJ4LMH00753VB8.html)

## 简单发送测试

文件 **sample_email.txt** 写入如下内容:

```
From: sender@robot.genee.cn
To: stenote@163.com
Subject: Hello World


Hello Stenote !
```
如上内容为上述接口中使用的 `data` 内容

执行如下命令进行邮件发送:

```
cat sample_email.txt | msmtp --debug stenote@163.com
```
