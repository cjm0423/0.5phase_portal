import os
from osclient import get_conn

IMAGE   = "3997c507-d72d-42a4-91a6-5d8686d3365e"   # cirros
FLAVOR  = "26684e06-96b9-48d3-b273-7eb520f271bf"   # cirros-tiny
NETWORK = "16dfa71b-2491-4368-b939-ac5afb47e08f"   # internal.network
NAME    = "sdk-probe-01"
KEY     = "sdk-probe-key"
KEYFILE = "/opt/su-portal/sdk-probe-key.pem"

conn = get_conn()

kp = conn.compute.find_keypair(KEY)
if kp is None:
    kp = conn.compute.create_keypair(name=KEY)
    with open(KEYFILE, "w") as f:
        f.write(kp.private_key)
    os.chmod(KEYFILE, 0o600)
    print("keypair created ->", KEYFILE)
else:
    print("keypair exists")

server = conn.compute.create_server(
    name=NAME,
    image_id=IMAGE,
    flavor_id=FLAVOR,
    networks=[{"uuid": NETWORK}],
    key_name=KEY,
    security_groups=[{"name": "default"}],
)
print("created :", server.id, server.status)

server = conn.compute.wait_for_server(server, status="ACTIVE", wait=300)
print("status  :", server.status)
print("fixed   :", server.addresses)