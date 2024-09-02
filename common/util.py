from datetime import datetime
from zoneinfo import ZoneInfo

from api.supabase.model.nfc import EntranceInfoDTO
from common.constants import *
from typing import TypeVar, Type, List, Optional, Dict
from pydantic import BaseModel
from postgrest.base_request_builder import APIResponse

class CommonUtil:
    @staticmethod
    def get_min_time_by_company_dvcd(company_dvcd):
        return MIN_TIME_POINT_BIG if company_dvcd in BIG_ROOM_COMPANY else MIN_TIME_POINT_SMALL

    @staticmethod
    def get_max_time_by_company_dvcd(company_dvcd):
        return MAX_TIME_POINT_BIG if company_dvcd in BIG_ROOM_COMPANY else MAX_TIME_POINT_SMALL

    @staticmethod
    def calculate_time_interval(given_time):
        current_time = datetime.now(ZoneInfo('Asia/Seoul'))
        return int(current_time.timestamp() - given_time.timestamp())

    @staticmethod
    def is_less_than_one_minute_interval(given_time):
        return CommonUtil.calculate_time_interval(given_time) < 60

class ScoreUtil:
    def __init__(self):
        pass

    @staticmethod
    def calculate_entrance_score(target_time):
        time_difference = int(datetime.now(ZoneInfo('Asia/Seoul')).timestamp() - target_time.timestamp())
        return time_difference * TIME_POINT_PER_SECOND

    @staticmethod
    def calculate_time_by_score(source_score, user_score):
        remain_score = source_score - user_score
        print(remain_score)
        remain_time_sec = remain_score / TIME_POINT_PER_SECOND
        print(remain_time_sec)
        return f"{int(remain_time_sec/60)}분 {int(remain_time_sec%60)}초"

    @staticmethod
    def check_min_stay_time(response:EntranceInfoDTO):
        print(f"[log] 경과 시간 확인 {ScoreUtil.calculate_entrance_score(response.created_at)}")
        print(f"[log] 각 사 최소 시간 {CommonUtil.get_min_time_by_company_dvcd(response.company_dvcd)}")

        return (ScoreUtil.calculate_entrance_score(response.created_at)
                > CommonUtil.get_min_time_by_company_dvcd(response.company_dvcd))

class MapperUtil:
    def __init__(self):
        pass
    # TypeVar로 DTO 클래스 타입을 정의
    T = TypeVar('T', bound=BaseModel)

    @staticmethod
    def multi_mapper(response: APIResponse, dto_class: Type[T]) -> Optional[List[T]]:
        return response.data

    @staticmethod
    def single_mapper(response: APIResponse, dto_class: Type[T]) -> Optional[T]:
        if not response.data:
            return None
        if len(response.data) > 1:
            raise ValueError("Expected a single result, but multiple records were found.")
        return dto_class(**response.data[0])

    @staticmethod
    def convert_dicts_to_lists(data: List[Dict]) -> List[List]:
        # 데이터가 비어 있는 경우 빈 리스트 반환
        if not data:
            return []

        # 딕셔너리의 키 순서를 유지하기 위해 첫 번째 딕셔너리의 키 순서를 사용
        keys = list(data[0].keys())

        # 각 딕셔너리의 값을 리스트로 변환
        result = [list(d.values()) for d in data]
        return result