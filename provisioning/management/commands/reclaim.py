from django.core.management.base import BaseCommand

from provisioning import services
from provisioning.models import Vm


class Command(BaseCommand):
    help = "ACTIVE 상태 VM 전체를 회수 예약함 (워커가 실제 삭제 수행)"

    def add_arguments(self, parser):
        parser.add_argument("--yes", action="store_true", help="확인 절차 생략")

    def handle(self, *args, **opts):
        targets = Vm.objects.filter(status=Vm.ACTIVE).order_by("slot_id")
        n = targets.count()

        if n == 0:
            self.stdout.write("회수 대상 없음")
            return

        self.stdout.write(f"회수 대상 {n}건:")
        for v in targets:
            self.stdout.write(f"  vm{v.slot_id}  {v.student_id}")

        if not opts["yes"]:
            if input(f"\n{n}건을 회수합니다. 계속하려면 'yes' 입력: ") != "yes":
                self.stdout.write("취소됨")
                return

        queued = services.request_delete_all()
        self.stdout.write(f"{len(queued)}건 예약 완료. 워커가 처리함")