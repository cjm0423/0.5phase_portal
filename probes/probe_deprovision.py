# probe_deprovision.py
import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

import time
from concurrent.futures import ThreadPoolExecutor

from django.db import connection
from provisioning.models import Slot, Vm
from provisioning.services import deprovision


def one(vm_id):
    try:
        t = time.time()
        deprovision(vm_id)
        return vm_id, "OK", time.time() - t
    except Exception as e:
        return vm_id, f"{type(e).__name__}", time.time() - t
    finally:
        connection.close()


ids = list(Vm.objects.filter(status=Vm.ACTIVE).values_list("id", flat=True))
t0 = time.time()
with ThreadPoolExecutor(max_workers=5) as ex:
    for vid, s, dt in ex.map(one, ids):
        print(f"vm{vid:<4} {s:<12} {dt:5.0f}s")

print(f"\ntotal {time.time()-t0:.0f}s")
print("Vm DELETED :", Vm.objects.filter(status=Vm.DELETED).count())
print("Slot FREE  :", Slot.objects.filter(status=Slot.FREE).count())
print("Vm 총건수   :", Vm.objects.count())