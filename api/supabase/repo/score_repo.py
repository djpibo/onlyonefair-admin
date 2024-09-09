from api.supabase.model.point import ConsumeInfoDTO, OliveInfoDTO
from api.supabase.model.quiz import ScoreInfoDTO, RankDTO
from common import constants
from common.constants import *
from common.util import MapperUtil, CommonUtil
from config.connect import connect_supabase


class ScoreRepository:
    def __init__(self):
        self.supabase = connect_supabase()

    def upsert_data_to_supabase(self, values, quiz_company):

        data_to_upsert = [
            {
                "id": row[QUIZ_SHEET_COL_INDEX_ID],
                "quiz_dvcd": QUIZ_DVCD_ROOM_QUIZ,
                "company_dvcd": quiz_company,
                "score": 20+row[QUIZ_SHEET_COL_INDEX_SCORE].split('/')[0].strip()
            }
            for row in values
        ]

        self.supabase.table("Score_Info").upsert(data_to_upsert, ignore_duplicates=True).execute()

    def get_user_current_point(self, peer_id):
        response = (
            self.supabase.table("Score_Info")
            .select("*")
            .eq("id", peer_id)
            .execute()
        )
        if response.data is None:
            return None
        return response.data

    def get_data_olive_info(self, peer_id):
        response = (
            self.supabase.table("Olive_Info")
            .select("*")
            .eq("id", peer_id)
            .execute()
        )
        return MapperUtil.single_mapper(response, OliveInfoDTO)

    def select_nfc_score(self, peer_id):
        response = (
            self.supabase.table("Score_Info")
            .select("score", count="exact")
            .eq("id", peer_id)
            .eq("quiz_dvcd", 3)
            .execute()
        )
        return MapperUtil.single_mapper(response, ScoreInfoDTO)

    # NFC 체류 시간 누적. 현재 점수 조회 후 가산
    def update_nfc_exist_time_score(self, source:ScoreInfoDTO):
        response = (
            self.supabase.table("Score_Info")
            .select("*")
            .eq("id", source.id)
            .eq("quiz_dvcd", source.quiz_dvcd)
            .eq("company_dvcd", source.company_dvcd)
            .execute()
        )
        before = MapperUtil.single_mapper(response, ScoreInfoDTO)
        # 최초 퇴장인 경우
        if before is None:
            new_score = source.score
        # N차 퇴장인 경우엔 합산
        else:
            new_score = min(source.score + before.score, CommonUtil.get_max_time_by_company_dvcd(source.company_dvcd))
        query = (
            self.supabase.table("Score_Info")
            .upsert(
                {"id": source.id,
                 "score": new_score,
                 "quiz_dvcd": source.quiz_dvcd,
                 "company_dvcd": source.company_dvcd})
            .execute()
        )

    # 입장 포인트 점수 부여
    def update_entrance_score(self, peer_id, company_dvcd):
        query = (
            self.supabase.table("Score_Info")
            .upsert(
                {"id": peer_id,
                 "score": constants.ENTER_POINT,
                 "quiz_dvcd": constants.QUIZ_DVCD_NFC_ENTRANCE,
                 "company_dvcd": company_dvcd}
                    , ignore_duplicates = True)
            .execute()
        )

    def fetch_score_from_supabase(self):
        # 실행할 SQL 쿼리
        sql_query = """
                    SELECT A.id
                          , SUM(SCORE) AS total_score
                          , RANK() OVER (ORDER BY SUM(SCORE) DESC) AS rank
                          , (SELECT NAME FROM "Peer_Info" B WHERE A.id = B.id) name
                          , (SELECT company FROM "Peer_Info" B WHERE A.id = B.id) company
                          , (SELECT SUM(SCORE) FROM "Score_Info" B WHERE A.id = B.id AND quiz_dvcd in (3,4)) AS room_score
                          , (SELECT SUM(SCORE) FROM "Score_Info" B WHERE A.id = B.id AND quiz_dvcd =2) AS quiz_score
                          , (SELECT SUM(SCORE) FROM "Score_Info" B WHERE A.id = B.id AND quiz_dvcd =14) AS photo_score
                          , (SELECT SUM(SCORE) FROM "Score_Info" B WHERE A.id = B.id AND quiz_dvcd =5) AS survey_score
                      FROM "Score_Info" A, "Peer_Info" B
                      WHERE A.id = B.id
                      GROUP BY A.id
                      ORDER BY SUM(SCORE) DESC
        """
        # SQL 쿼리 실행
        response = self.supabase.rpc('execute_query', {'query': sql_query}).execute()
        return MapperUtil.multi_mapper(response, RankDTO)

    def insert_used_point(self, consume_info:ConsumeInfoDTO):
        (self.supabase.table("Consume_Info")
         .upsert({"id": consume_info.id,
                  "consume_dvcd": consume_info.consume_dvcd,
                  "used_score": consume_info.used_score}
                 )
         .execute())

    def get_total_used_score(self, peer_id):
        return (self.supabase.table("Consume_Info")
                .select("used_score")
                .eq("id", peer_id)
                .eq("cancel_yn", False)
                .execute()).data

    def update_olive_data(self, olive_info):
        self.supabase.table("Olive_Info").update({"used_count": olive_info.used_info}).eq("id", olive_info.peer_id).execute()

    # 연속 차감 여부 확인
    def check_latest_consume(self, peer_id):
        response = (
            self.supabase.table("Consume_Info")
            .select("*")
            .eq("id", peer_id)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        return MapperUtil.single_mapper(response, ConsumeInfoDTO)

    def get_exp_score(self, score_dto:ScoreInfoDTO):
        return (self.supabase.table("Score_Info")
                .select("score")
                .eq("id", score_dto.id)
                .eq("company_dvcd", score_dto.company_dvcd)
                .eq("quiz_dvcd", score_dto.quiz_dvcd)
                .execute()).data

    def get_used_point_by_id(self, peer_id):
        response = self.supabase.table("Consume_Info").select("used_score").eq("id", peer_id).execute()
        if response.data is None:
            return None
        return response.data