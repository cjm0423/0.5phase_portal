import subprocess, time
from osclient import get_conn

SERVER = "f2a4fce2-4248-4d09-ae8e-12b821ec1555"
FIP    = "192.168.100.28"
KEYFILE = "/opt/su-portal/sdk-probe-key.pem"

conn = get_conn()

port = next(conn.network.ports(device_id=SERVER))
print("port    :", port.id, port.fixed_ips)

fip = next(conn.network.ips(floating_ip_address=FIP))
print("fip     :", fip.id, fip.status)

fip = conn.network.update_ip(fip, port_id=port.id)
print("attached:", fip.floating_ip_address, "->", fip.port_id)

for i in range(30):
    r = subprocess.run(
        ["ssh", "-i", KEYFILE, "-o", "StrictHostKeyChecking=no",
         "-o", "UserKnownHostsFile=/dev/null", "-o", "ConnectTimeout=3",
         f"cirros@{FIP}", "hostname"],
        capture_output=True, text=True,
    )
    if r.returncode == 0:
        print(f"ssh ok after {i*5}s :", r.stdout.strip())
        break
    time.sleep(5)
else:
    print("ssh failed")
    print(r.stderr.strip())