import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from collections import Counter
from concurrent.futures import ThreadPoolExecutor

from django.db import connection

from provisioning.models import Slot, Vm
from provisioning.services import reserve

N_THREADS = 50          # 슬롯 45개보다 많게


def one(i):
    try:
        vm = reserve(f"s{i:03d}")
        return vm.slot_id if vm else None
    finally:
        connection.close()          # 스레드별 연결 정리


with ThreadPoolExecutor(max_workers=N_THREADS) as ex:
    got = list(ex.map(one, range(N_THREADS)))

ok = [x for x in got if x is not None]
dup = [n for n, c in Counter(ok).items() if c > 1]

print("성공        :", len(ok), "/", N_THREADS)
print("실패(None)  :", len(got) - len(ok))
print("중복 배정    :", dup or "없음")
print("배정 슬롯    :", sorted(ok) == list(range(1, 46)))
print("DB TAKEN    :", Slot.objects.filter(status=Slot.TAKEN).count())
print("DB Vm       :", Vm.objects.count())