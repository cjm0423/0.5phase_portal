import subprocess, time
from osclient import get_conn

IMAGE   = "36fdb4fc-9d15-415f-936f-0948cb98bdb1"   # ubuntu-24.04
FLAVOR  = "f62c57b7-de32-4961-9ed5-ae3950a593f7"   # bastion-small
NETWORK = "16dfa71b-2491-4368-b939-ac5afb47e08f"
NAME    = "sdk-probe-02"
KEY     = "sdk-probe-key"
KEYFILE = "/opt/su-portal/sdk-probe-key.pem"
FIP     = "192.168.100.179"

conn = get_conn()
t0 = time.time()

server = conn.compute.create_server(
    name=NAME,
    image_id=IMAGE,
    flavor_id=FLAVOR,
    networks=[{"uuid": NETWORK}],
    key_name=KEY,
    security_groups=[{"name": "default"}],
)
server = conn.compute.wait_for_server(server, status="ACTIVE", wait=600)
t_active = time.time() - t0
print(f"ACTIVE at {t_active:.0f}s  id={server.id}")

port = next(conn.network.ports(device_id=server.id))
fip  = next(conn.network.ips(floating_ip_address=FIP))
conn.network.update_ip(fip, port_id=port.id)
print(f"FIP attached at {time.time()-t0:.0f}s")

for user in ("ubuntu", "root"):
    for i in range(60):
        r = subprocess.run(
            ["ssh", "-i", KEYFILE, "-o", "StrictHostKeyChecking=no",
             "-o", "UserKnownHostsFile=/dev/null", "-o", "ConnectTimeout=3",
             f"{user}@{FIP}", "cloud-init status --wait; hostname; id"],
            capture_output=True, text=True,
        )
        if r.returncode == 0:
            print(f"\nSSH ok as '{user}' at {time.time()-t0:.0f}s "
                  f"(ACTIVE +{time.time()-t0-t_active:.0f}s)")
            print(r.stdout.strip())
            raise SystemExit
        time.sleep(5)
    print(f"'{user}' failed: {r.stderr.strip()[:200]}")