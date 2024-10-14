#!/usr/bin/env python
# coding: utf-8
import requests
import json
import os

EMAIL = os.environ["EMAIL"]
KEY = os.environ["KEY"]
TG_TOKEN = os.environ["TG_TOKEN"]
TG_CHAT_ID = os.environ["TG_CHAT_ID"]
DOMAINS = os.environ["DOMAINS"]

class CloudFlareDDNSUpdater:
    def __init__(self, email_str, token_str):
        self.headers = {
            "X-Auth-Email": email_str,
            "X-Auth-Key": token_str,
            "Content-Type": "application/json",
        }

    def get_zone_id(self, domain):
        url = 'https://api.cloudflare.com/client/v4/zones'
        req = requests.get(url=url, data=None, headers=self.headers)
        res = json.loads(req.text)
        for i in res.get('result'):
            if i.get('name') == domain:
                return i.get('id')

    def get_dns_record_id(self, domain_id, record):
        url = f'https://api.cloudflare.com/client/v4/zones/{domain_id}/dns_records'
        req = requests.get(url=url, data=None, headers=self.headers)
        res = json.loads(req.text)
        for i in res.get('result'):
            if i.get('name') == record:
                return i.get('id')

    def update_a_record(self, domain, content):
        zone = domain.split('.')
        zone = zone[1]+'.'+zone[2]
        zone_id = self.get_zone_id(zone)
        record_id = self.get_dns_record_id(zone_id, domain)
        url = f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}'
        data = {
            'type': 'A',
            'name': domain,
            'content': content,
            'ttl': 60*5,
            'proxied': False,
        }
        req = requests.put(url=url, data=json.dumps(data), headers=self.headers)
        return json.loads(req.text)


def get_ip():
    url = 'https://api.hostmonit.com/get_optimization_ip'
    headers = {'Content-type': 'application/json;charset=UTF-8'}
    data = {'key': 'iDetkOys'}
    req = requests.post(url=url, data=json.dumps(data), headers=headers, timeout=10)
    return json.loads(req.text)


if __name__ == '__main__':
    ret = get_ip()
    if ret is not None:
        if ret['code'] == 200:
            yd = None
            dx = None
            lt = None
            for item in ret['info']:
                if item['line'] == 'CM':
                    if yd is None:
                        yd = item
                    else:
                        if yd['latency'] > item['latency']:
                            yd = item
                elif item['line'] == 'CT':
                    if dx is None:
                        dx = item
                    else:
                        if dx['latency'] > item['latency']:
                            dx = item
                elif item['line'] == 'CU':
                    if lt is None:
                        lt = item
                    else:
                        if lt['latency'] > item['latency']:
                            lt = item
            updater = CloudFlareDDNSUpdater(EMAIL, KEY)
            #[
            #    {"name":"yd.eoos.work", "type":"CM"},
            #    {"name":"dx.eoos.work", "type":"CT"},
            #    {"name":"lt.eoos.work", "type":"CU"}
            #]
            urls = json.loads(DOMAINS)
            message = "更新优选IP\n"
            for url in urls:
                if url['type'] == 'CM':
                    updater.update_a_record(url['name'], yd['ip'])
                    message += url['name']+" == "+yd['ip']+"\n"
                elif url['type'] == 'CT':
                    updater.update_a_record(url['name'], dx['ip'])
                    message += url['name']+" == "+dx['ip']+"\n"
                elif url['type'] == 'CU':
                    updater.update_a_record(url['name'], lt['ip'])
                    message += url['name']+" == "+lt['ip']+"\n"
            headers = {'Content-type': 'application/json;charset=UTF-8'}
            data = {
                'chat_id': TG_CHAT_ID,
                'parse_mode': 'HTML',
                'text': message,
            }
            url = f'https://tg.eyoung.work/bot{TG_TOKEN}/sendMessage'
            requests.post(url=url, data=json.dumps(data), headers=headers)
            print('操作完成')
        else:
            print(ret['info'])
