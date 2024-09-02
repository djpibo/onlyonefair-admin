from api.supabase.model.common import CommonCodeDTO
from common.util import MapperUtil
from config.connect import connect_supabase

class CommonRepository:
    def __init__(self):
        self.supabase = connect_supabase()

    # command.py arguments 검증에 사용
    def get_cmn_code_with_nm_desc(self, cmn_nm, cmn_desc):
        response = (
            self.supabase.table("Common_Code")
            .select("*")
            .eq("cmn_nm", cmn_nm)
            .eq("cmn_desc", cmn_desc)
            .execute()
        )
        return MapperUtil.single_mapper(response, CommonCodeDTO)

    def get_company_code(self, company_name):
        response = (
            self.supabase.table("Common_Code")
            .select("*")
            .eq("cmn_nm", "회사명")
            .eq("cmn_desc", company_name)
            .execute()
        )
        return MapperUtil.single_mapper(response, CommonCodeDTO)

    def get_enter_code(self, enter):
        response = (
            self.supabase.table("Common_Code")
            .select("*")
            .eq("cmn_nm", "입퇴장구분코드")
            .eq("cmn_desc", enter)
            .execute()
        )
        return MapperUtil.single_mapper(response, CommonCodeDTO)

    def get_common_by_cmn_id(self, cmn_id):
        response = (
            self.supabase.table("Common_Code")
            .select("*")
            .eq("id", cmn_id)
            .execute()
        )
        return MapperUtil.single_mapper(response, CommonCodeDTO)

    def insert_tag_count(self, param):
        self.supabase.table("Count_Info").insert({"id": param.id}).execute()

    def upsert_olive_count(self, olive_info):
        self.supabase.table("Olive_Info").upsert({"id":olive_info.id, "count": olive_info.count}).execute()
