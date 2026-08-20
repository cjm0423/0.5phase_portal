import time
from concurrent.futures import ThreadPoolExecutor
from osclient import get_conn, vm

NS = [2, 3, 4, 5, 6]
KEYFILE = "/opt/su-portal/sdk-probe-key.pem"

t0 = time.time()


def one(n):
    conn = get_conn()
    t = time.time()
    try:
        vm.create(conn, n, KEYFILE)
        return n, "OK", time.time() - t
    except Exception as e:
        return n, f"{type(e).__name__}: {e}"[:60], time.time() - t


with ThreadPoolExecutor(max_workers=5) as ex:
    rows = list(ex.map(one, NS))

for n, status, dt in rows:
    print(f"vm{n:<3} {status:<24} {dt:6.0f}s")

print(f"\ntotal {time.time()-t0:.0f}s")
print("ok :", sum(1 for _, s, _ in rows if s == "OK"), "/", len(NS))