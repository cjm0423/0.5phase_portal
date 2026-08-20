from osclient import get_conn

conn = get_conn()
pid = conn.current_project_id
print("project_id :", pid)

print("\n=== NEUTRON QUOTA (raw) ===")
q = conn.network.get_quota(pid)
for k, v in sorted(q.to_dict().items()):
    print(f"{k:24} {v}")

print("\n=== ROUTERS ===")
for r in conn.network.routers():
    print(f"{r.name:20} {r.id}  project={r.project_id}")
    print(f"   gateway: {r.external_gateway_info}")
    for p in conn.network.ports(device_id=r.id):
        print(f"   port: {p.device_owner:28} net={p.network_id}")

print("\n=== SG (admin only) ===")
for s in conn.network.security_groups(project_id=pid):
    print(f"{s.name:15} {s.id}")
    for r in s.security_group_rules:
        if r["direction"] == "ingress":
            print(f"   {r['protocol']} {r['port_range_min']}-{r['port_range_max']} "
                  f"from {r.get('remote_ip_prefix')} {r.get('remote_group_id')}")

print("\n=== EXISTING SERVERS ===")
for s in conn.compute.servers():
    print(f"{s.name:25} {s.status:8} {s.id}")

print("\n=== FIP ===")
for f in conn.network.ips():
    print(f"{f.floating_ip_address:18} {f.status:8} port={f.port_id}")