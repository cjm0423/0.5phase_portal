from django.core.management.base import BaseCommand

from provisioning import services


class Command(BaseCommand):
    help = "빈 슬롯에서 n개 VM 발급을 예약함 (워커가 실제 생성 수행)"

    def add_arguments(self, parser):
        parser.add_argument("-n", "--count", type=int, default=1,
                            help="발급할 VM 수 (기본 1)")
        parser.add_argument("--student", type=str, default="",
                            help="student_id 꼬리표 (선택)")

    def handle(self, *args, **opts):
        n = opts["count"]
        queued = []

        for _ in range(n):
            rec = services.reserve(opts["student"])
            if rec is None:
                break
            queued.append(rec)
            self.stdout.write(f"  예약 vm{rec.slot_id}")

        if not queued:
            self.stdout.write("빈 슬롯 없음")
            return

        if len(queued) < n:
            self.stdout.write(f"슬롯 부족: 요청 {n}건 중 {len(queued)}건만 예약됨")
        else:
            self.stdout.write(f"{len(queued)}건 예약 완료. 워커가 처리함")