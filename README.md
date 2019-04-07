# Reptile
# 报错requests.exceptions.SSLError: HTTPSConnectionPool
# 可能原因有：
# 1. 请求过于频繁，被暂时封IP。解决方法：用try: except: 结构加入time.sleep()
# 2. 使用代理proxy
# 3. 指定headers的User-Agent时,服务器会重定向到https的网址。解决方法：直接关闭证书验证request.get(......,verify=False)
