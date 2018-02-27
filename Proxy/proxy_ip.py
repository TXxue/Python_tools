# -*- coding: utf-8 -*-
import requests
import re
import os
import json
from multiprocessing.dummy import Pool


class proxyIPCheck(object):
    def __init__(self):
        self.proxy_addr = "http://www.gatherproxy.com/zh/"
        self.check_addr = "http://ip.chinaz.com/getip.aspx"
        self.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36"
        }

    def proxyIPGet(self):
        res = requests.get(self.proxy_addr, headers=self.headers, timeout=30)
        proxy_index = res.text
        proxy_rule = r'gp.insertPrx\((.*?)\)'
        proxy_json = re.findall(proxy_rule, proxy_index, re.S | re.M)
        proxy_ips = []
        for p in proxy_json:
            ip = json.loads(p)["PROXY_IP"]
            port = json.loads(p)["PROXY_PORT"]
            ip_info = "{ip}:{port}".format(ip=ip, port=int(port, 16))
            proxy_ips.append(ip_info)
        return proxy_ips

    def __checkip(self, ip):
        proxies = {"http": "http://" + ip}
        s = requests.session()
        s.keep_alive = False
        try:
            res = s.get(self.check_addr, proxies=proxies, timeout=5)
            if "window.location" not in res.text:
                return ip
        except BaseException:
            pass

    def validIPGet(self, proxyinfo):
        thread = len(proxyinfo)
        pool = Pool(thread)
        ips = pool.map(self.__checkip, proxyinfo)
        pool.close()
        pool.join()
        ips = [i for i in ips if i]
        return ips

    def saveIP(self, ips, fpath, fname):
        if not os.path.exists(fpath):
            os.makedirs(fpath)
        try:
            with open(fpath+fname, 'wb') as f:
                for i in ips:
                    f.write(i+'\r\n')
            return True
        except Exception as e:
            print e
            return False


def main():
    p = proxyIPCheck()

    print("Gets ip list...")
    proxyinfo = p.proxyIPGet()

    print("Check ip...")
    ips = p.validIPGet(proxyinfo)

    print("Save to proxyip.txt")
    ret = p.saveIP(ips, './proxy_file/', 'proxyip.txt')
    if not ret:
        print "Save to ./proxy_file/proxyip.txt failed!!!"


if __name__ == "__main__":
    main()