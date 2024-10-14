**使用教程**

在secret中填写

>EMAIL: CF账号
>
>KEY: CF的GAK
>
>DOMAINS: 三网域名数组，CF里的域名
>
>TG_TOKEN: TG的TOKEN，不填不发送
>
>TG_CHAT_ID: TG的chat_id

三网域名数组例子：

``` bash
[
    {"name":"移动域名", "type":"CM"},
    {"name":"电信域名", "type":"CT"},
    {"name":"联通域名", "type":"CU"}
]
```

不填某网不设置
