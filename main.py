import sys

from injector import Injector
from command import Commander
from inject_module import Euljiro

injector = Injector([Euljiro()])
commander = injector.get(Commander)

def main():

    if sys.argv[1] == "배치":
        # 대표작 사전 설문(9), 각 사별 퀴즈(6) -----집계-----> 전 사원 포인트 현황(1)
        print(f"[log] 시트 업로드 배치 수행")
        commander.start_sheet_data_batch()

    if sys.argv[1] == "마감":
        print(f"[log] 마감 배치 수행")
        commander.force_exit()

if __name__ == "__main__":
    main()