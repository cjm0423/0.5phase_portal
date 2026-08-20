import time
from osclient import get_conn

SERVER = "f2a4fce2-4248-4d09-ae8e-12b821ec1555"
PORT   = "6ae68064-fc2b-4063-bda2-85e5e0a6d88c"
FIP    = "192.168.100.28"

conn = get_conn()

before = len(list(conn.network.ports()))
print("ports before :", before)

conn.compute.delete_server(SERVER)
conn.compute.wait_for_delete(conn.compute.get_server(SERVER), wait=180)
print("server deleted")

time.sleep(5)

print("ports after  :", len(list(conn.network.ports())))

p = conn.network.find_port(PORT)
print("port survives:", p is not None)

f = next(conn.network.ips(floating_ip_address=FIP), None)
if f is None:
    print("FIP DELETED  <- 문제")
else:
    print(f"FIP alive    : {f.floating_ip_address} status={f.status} port={f.port_id}")