import subprocess
import ipaddress
from flask import Flask, render_template
import threading

app = Flask(__name__)

# 存储IP状态的字典，初始状态为None
ip_status = {}

# 定义目标C段IP地址范围
target_cidr = "194.233.84.1/24"  # 例如，将其替换为您要监测的C段IP范围

# 解析C段IP地址范围
network = ipaddress.IPv4Network(target_cidr, strict=False)

def check_ip(ip):
    global ip_status
    try:
        # 使用nmap扫描指定IP地址
        result = subprocess.run(['nmap', '-sn', ip], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if "Host is up" in result.stdout:
            ip_status[ip] = "在线"
        else:
            ip_status[ip] = "离线"
    except Exception as e:
        # 处理错误
        ip_status[ip] = "错误"

def scan_ips():
    global network
    threads = []
    for host_ip in network.hosts():
        host_ip = str(host_ip)
        thread = threading.Thread(target=check_ip, args=(host_ip,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

@app.route('/')
def index():
    global ip_status
    scan_ips()
    return render_template('index.html', ip_status=ip_status)

if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True, port=5800)

