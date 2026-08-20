# probe_provision.py
import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

import time
from concurrent.futures import ThreadPoolExecutor

from django.db import connection
from provisioning.models import Slot, Vm
from provisioning.services import reserve, provision

# 2~6만 열어둠
Slot.objects.update(status=Slot.TAKEN)
Slot.objects.filter(n__in=[2, 3, 4, 5, 6]).update(status=Slot.FREE)


def one(i):
    try:
        rec = reserve(f"s{i:03d}")
        if rec is None:
            return None, "no slot", 0
        t = time.time()
        try:
            provision(rec.id)
            return rec.slot_id, "OK", time.time() - t
        except Exception as e:
            return rec.slot_id, f"{type(e).__name__}"[:40], time.time() - t
    finally:
        connection.close()


t0 = time.time()
with ThreadPoolExecutor(max_workers=5) as ex:
    rows = list(ex.map(one, range(5)))

for n, s, dt in rows:
    print(f"slot{str(n):<4} {s:<20} {dt:5.0f}s")

print(f"\ntotal {time.time()-t0:.0f}s")
for v in Vm.objects.all():
    print(v.slot_id, v.student_id, v.status, v.server_id)