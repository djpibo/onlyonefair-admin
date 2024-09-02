import math

from api.supabase.model.common import LoginDTO
from api.supabase.model.point import ConsumeInfoDTO
from api.supabase.model.quiz import ScoreInfoDTO
from common.constants import *
from common.util import ScoreUtil, CommonUtil
from service.common_service import CommonMgr
from service.point_service import PointMgr
from service.room_stay_service import ExitMgr, ScoreMgr, EnterMgr


class Commander:
    def __init__(self, enter_mgr: EnterMgr, exit_mgr: ExitMgr, score_mgr: ScoreMgr, common_mgr: CommonMgr, point_mgr: PointMgr):
        self.enter_mgr = enter_mgr
        self.exit_mgr = exit_mgr
        self.score_mgr = score_mgr
        self.common_mgr = common_mgr
        self.point_mgr = point_mgr

    def start_sheet_data_batch(self):
        self.point_mgr.upload_room_quiz_point()

    def force_exit(self):
        # 최초 입장인 경우 + 최소 시간 이하면 0점 처리
        # 나머지는 동일
        # 데이터를 받아와서 한 건씩 진행하는 것으로 계산

        cnt_zero = 0
        cnt_full = 0
        cnt_normal = 0

        datas = self.enter_mgr.get_entered_users()
        for item in datas:
            login_dto = LoginDTO(peer_id=item['id'], argv_company_dvcd=item['company_dvcd'], enter_dvcd=item['enter_dvcd'])
            recent_enter_info = self.enter_mgr.get_latest_enter(login_dto)

            # 체류 시간 계산
            current_exp_point = ScoreUtil.calculate_entrance_score(recent_enter_info.created_at)
            # 각 사별 상한, 최소 포인트
            min_point = CommonUtil.get_min_time_by_company_dvcd(login_dto.argv_company_dvcd)
            max_point = CommonUtil.get_max_time_by_company_dvcd(login_dto.argv_company_dvcd)

            # 상한 시간 검증을 위한 이전 누적 시간 집계
            score_info_dto = ScoreInfoDTO(
                id=login_dto.peer_id, quiz_dvcd=QUIZ_DVCD_NFC_EXIST_TIME, company_dvcd=login_dto.argv_company_dvcd, score=0)
            bf_exp_point = self.score_mgr.get_exp_score(score_info_dto)

            # 동적 분기 처리를 위한 변수 초기화
            update_point = 0

            # 최초 입장이면서 최소 시간을 지키지 못한 경우
            if login_dto.enter_dvcd == ENTER_DVCD_ENTRANCE and current_exp_point < min_point:
                update_point = 0
                cnt_zero = cnt_zero + 1
                print(f"[log] {login_dto.peer_id} 최소 시간 미달, 0점으로 퇴장 처리")

            # 이미 만점으로 입장한 경우 or 만점을 넘은 경우, 상한 포인트로 제한
            elif current_exp_point >= max_point:
                update_point = max_point
                cnt_full = cnt_full + 1
                print(f"[log] {login_dto.peer_id} {max_point}으로 퇴장 처리")

            # 정상 시간 범위
            else:
                update_point = current_exp_point
                cnt_normal = cnt_normal + 1
                print(f"[log] {login_dto.peer_id} {update_point}으로 퇴장 처리")

            self.exit_mgr.set_enter_exit(recent_enter_info)  # latest 입장 > 퇴장 여부 True
            self.exit_mgr.set_force_exit_true(recent_enter_info)  # 마감으로 퇴장 처리
            stay_score_info = ScoreInfoDTO(
                id=login_dto.peer_id,
                quiz_dvcd=QUIZ_DVCD_NFC_EXIST_TIME,
                company_dvcd=login_dto.argv_company_dvcd,
                score=update_point,
            )
            self.score_mgr.set_score(stay_score_info)

        print(f"[log] Total:{len(datas)},\n0점 처리:{cnt_zero}\n만점 처리:{cnt_full}\n정상 처리:{cnt_normal}")

    # 포인트 차감
    def point_consumer(self, login_dto):
        consumer = login_dto.peer_id

        # 1 연속 거래 방지
        if CommonUtil.is_less_than_one_minute_interval(self.point_mgr.get_latest_consume(login_dto).created_at):
            print(f"[log] 연속 거래 방지")

        # 2 누적 포인트에 기반해서 계산
        current_point = self.score_mgr.get_current_point(LoginDTO(peer_id=consumer, argv_company_dvcd=99))
        current_count = math.floor(current_point / 800)

        # 2-1 조건 검증
        if current_point > CONSUME_LUCKY_POINT:

            # 3 포인트 차감 처리
            consume_dto = ConsumeInfoDTO(id=consumer, consume_dvcd=CONSUME_PHOTO_DVCD, used_score=CONSUME_PHOTO_POINT)
            self.point_mgr.consume_point(consume_dto)

            # 4 화면 촬영권 표시
            re_point = current_point - self.score_mgr.get_total_used_score(consumer)
            print(f"[log] 총 사용 촬영권 {current_count}, 현재 잔여 촬영권 {math.floor(re_point)}")

        else:
            print(f"[log] 포인트가 부족합니다 :<")