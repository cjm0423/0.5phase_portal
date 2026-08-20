from osclient import get_conn

conn = get_conn()

print("=== IMAGES ===")
for i in conn.image.images():
    print(f"{i.name:30} {i.id}  {i.status:8} min_disk={i.min_disk} min_ram={i.min_ram}")

print("\n=== FLAVORS ===")
for f in conn.compute.flavors():
    print(f"{f.name:20} {f.id}  vcpu={f.vcpus} ram={f.ram} disk={f.disk}")

print("\n=== NETWORKS ===")
for n in conn.network.networks():
    print(f"{n.name:25} {n.id}  external={n.is_router_external} subnets={n.subnet_ids}")

print("\n=== KEYPAIRS ===")
for k in conn.compute.keypairs():
    print(f"{k.name:25} {k.fingerprint}")

print("\n=== SECURITY GROUPS ===")
for s in conn.network.security_groups():
    print(f"{s.name:25} {s.id}  rules={len(s.security_group_rules)}")

print("\n=== NEUTRON QUOTA ===")
q = conn.network.get_quota(conn.current_project_id)
for k in ("port", "floatingip", "security_group", "security_group_rule", "network", "subnet", "router"):
    print(f"{k:22} {getattr(q, k, None)}")