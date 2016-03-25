# postoffice 设计文档

该文档主要用于说明 `postoffice` 的设计

## 设计简述

`postoffice` 为邮件过滤、合并、递送方, 此处主要由如下几部分组成:

* `doorman`
* `dispatcher`
* `worker`

---

`doorman` 提供 **HTTP** 接口, 进行 `mailman` 发送过来的数据结构的验证、处理, `doorman` 在验证通过后通过 `MQ` 系统发送数据到 `dispatcher`

---

`MQ` 系统选用 `beanstalkd`, 提供队列服务, 避免并发过高的问题

---

`dispatcher` 为分发器, 通过对接 `MQ` 系统, 将来自队列的系统进行分发到不同的 `worker`

---

`worker` 根据具体根据 `dispatcher` 分发过来的数据进行处理, 然后根据处理情况重新反馈给 `dispatcher` （通过 MQ）, 或者不予返回, 等待后续处理. 


## 数据结构

分为如下几个需要说明的数据结构:

* `doorman` 通过 `MQ` 系统推送到 `dispatcher` 的数据结构
* `dispatcher` 分发到各个 `worker` 的数据结构
* 各个 `worker` 反馈给 `dispatcher` 的数据结构

### doorman 通过 MQ 系统推送到 dispatcher 的数据结构

数据为 json 结构, 如下:

```
{
	'from': 'sender@robot.genee.cn',
	'to': ["stenote@163.com"],
	'data': '
		From: sender@robot.genee.cn
		To: stenote@163.com
		Subject: Hello World

		Hello World
	',
	'extra': {
	}
}
```

* `from` 为发件人地址
* `to` 为收件人地址合集
* `data` 为邮件正文
* `extra` 为邮件 worker 处理后的附加信息, 可有可无,  `worker` 可对 `extra` 写自己需要的数据, 避免多次 dispatcher 后重复分发处理的情况产生.

### dispatcher 分发到各个 worker 的数据结构


数据为 `json` 结构, 如下:

```
{
	'from': 'sender@robot.genee.cn',
	'to': ["stenote@163.com"],
	'data': '
		From: sender@robot.genee.cn
		To: stenote@163.com
		Subject: Hello World

		Hello World
	'
}
```

* `from` 为发件人地址
* `to` 为收件人地址合集
* `data` 为邮件正文


### 各个 worker 反馈给 dispatcher 的数据结构

数据为 `json` 结构, 如下:

```
{
	'from': 'sender@robot.genee.cn',
	'to': ["stenote@163.com"],
	'data': '
		From: sender@robot.genee.cn
		To: stenote@163.com
		Subject: Hello World

		Hello World
	',
	'last_worker': 'merge',
	'result': 'pass',
	'extra': {}
}
```

* `from` 为发件人地址
* `to` 为收件人地址合集
* `data` 为邮件正文
* `processed` 为已处理了的 `worker`, 用于 `dispatcher` 进行判断如何进行后续工作
* `last_worker` 为最后一个进行处理的 `worker` 的名称
* `result` 为最后一个进行处理的 `worker` 的结果, 目前有如下几种结果:
	* `skip`, 当前 `worker` 不予处理该邮件, 请 `dispatcher` 重新分发、处理
	* `trash`, 请 `dispatcher` 扔该邮件到垃圾桶
	* `pass`, 处理完毕, 请 `dispatcher` 递交到其他 `worker` 进行后续处理
* `extra` 为邮件 worker 处理后的附加信息, 可有可无,  `worker` 可对 `extra` 写自己需要的数据, 避免多次 dispatcher 后重复分发处理的情况产生.

## 举例


假设有如下几个 `worker`:

* **worker0**, 垃圾邮件过滤器的 worker
* **worker1**, 修改 subject 的 worker
* **worker2**, 邮件内容后缀增加附加信息的 worker
* **worker4**, 进行限流的 worker
* **worker5**, 垃圾回收的 worker
* **worker6**, 邮件发送的 worker

### 普通邮件请求

一次请求过来后, `dispatcher` 按照过滤顺序进行分发:

* `dispatcher` 先分发到 **worker0**, 该 **worker** 处理后, 返回给 `dispatcher`
* `dispatcher` 重新分发, 分发到 **worker1**, 该 **worker** 处理后, 返回给 `dispatcher`,
* `dispatcher` 重新分发, 分发到 **worker2**, 该 **worker** 处理后,  返回给 `dispatcher`
* `dispatcher` 重新分发, 分发到 **worker4**, 该 **worker** 处理后,  返回给 `dispatcher`
* `dispatcher` 重新分发, 分发到 **worker6**, 该 **worker** 处理后, 不会有任何反馈给 `dispatcher`

### 垃圾邮件请求


一次请求过来后, `dispatcher` 按照过滤顺序进行分发:

* `dispatcher` 先分发到 **worker0**, 该 **worker** 处理后, 返回给 `dispatcher`, 同时告之 `dispatcher`, 请把这封邮件发给垃圾回收的 **worker**
* `dispatcher` 重新分发, 分发到 **worker6**, 该 **worker** 处理后, 不会有任何反馈给 `dispatcher`


### 限流邮件请求

* `dispatcher` 先分发到 **worker0**, 该 **worker** 处理后, 返回给 `dispatcher`
* `dispatcher` 重新分发, 分发到 **worker1**, 该 **worker** 处理后, 返回给 `dispatcher`,
* `dispatcher` 重新分发, 分发到 **worker2**, 该 **worker** 处理后,  返回给 `dispatcher`
* `dispatcher` 重新分发, 分发到 **worker4**, 该 **worker** 处理后, 进行限流, 等待一段时间后, 发送给 `dispatcher`
* `dispatcher` 重新分发, 分发到 **worker6**, 该 **worker** 处理后, 不会有任何反馈给 `dispatcher`
