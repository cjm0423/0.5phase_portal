import subprocess, time
from osclient import get_conn
import base64

IMAGE   = "36fdb4fc-9d15-415f-936f-0948cb98bdb1"
FLAVOR  = "f62c57b7-de32-4961-9ed5-ae3950a593f7"
NETWORK = "16dfa71b-2491-4368-b939-ac5afb47e08f"
NAME    = "sdk-probe-03"
KEY     = "sdk-probe-key"
KEYFILE = "/opt/su-portal/sdk-probe-key.pem"
FIP     = "192.168.100.181"

USER_DATA = """#cloud-config
users:
  - name: student
    sudo: ALL=(ALL) NOPASSWD:ALL
    shell: /bin/bash
    ssh_authorized_keys:
      - {pubkey}

write_files:
  - path: /etc/su-cloud-probe
    content: "user_data applied"
"""

conn = get_conn()

pubkey = conn.compute.get_keypair(KEY).public_key
ud = USER_DATA.format(pubkey=pubkey)

t0 = time.time()
server = conn.compute.create_server(
    name=NAME,
    image_id=IMAGE,
    flavor_id=FLAVOR,
    networks=[{"uuid": NETWORK}],
    key_name=KEY,
    security_groups=[{"name": "default"}],
    user_data=base64.b64encode(ud.encode()).decode(),
)
server = conn.compute.wait_for_server(server, status="ACTIVE", wait=600)
print(f"ACTIVE at {time.time()-t0:.0f}s  id={server.id}")

port = next(conn.network.ports(device_id=server.id))
fip  = next(conn.network.ips(floating_ip_address=FIP))
conn.network.update_ip(fip, port_id=port.id)

for i in range(60):
    r = subprocess.run(
        ["ssh", "-i", KEYFILE, "-o", "StrictHostKeyChecking=no",
         "-o", "UserKnownHostsFile=/dev/null", "-o", "ConnectTimeout=3",
         f"student@{FIP}",
         "cloud-init status --wait; id; cat /etc/su-cloud-probe"],
        capture_output=True, text=True,
    )
    if r.returncode == 0:
        print(f"\nSSH ok as 'student' at {time.time()-t0:.0f}s")
        print(r.stdout.strip())
        break
    time.sleep(5)
else:
    print("student login failed:", r.stderr.strip()[:200])