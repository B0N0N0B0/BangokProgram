import random,os,sys,csv,shutil,datetime
import tkinter as tk
import tkinter.messagebox
from tkinter.font import Font
from tkinter import filedialog
import tkinter.ttk
from PIL import ImageTk,Image,ImageFont,ImageDraw
from Crypto.Cipher import AES
import base64
import hashlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import configparser as cp



# tkinter api
# https://076923.github.io/posts/Python-tkinter-21/

version = "0.00.17 - Development"
_title = "반곡고등학교 매점 관리 프로그램"
title = "{} / {}".format(_title,version)
ENCRYPT_KEY = "------------" # 보안상의 이유로 블라인드 처리됨
backup_key = "-------------------" # 보안상의 이유로 블라인드 처리됨
backup_key2 = "------------------" # 보안상의 이유로 블라인드 처리됨

sz = [1920,1080]
exit = False
pwd = ""
popup = {
    "main-pwch" : False,
    "pd-add" : False,
    "pd-modify" : False
}

ProductList = dict()
UsingLog = dict()
StudentList = dict()
Baled_StudentList = dict()
std_balances = list()
WarningList = dict()
_Warnings = list()
stockLogList = dict()

PDdataLen = int()
LogdataLen = int()
STdataLen = int()

pd_btn_list = dict()
pd_selected = list()
mdfy_index = int()
pd_page = 1
pd_page_max = int()
_pdaddimg = str()
pd_modify = [False,False,False]
pd_md_save = False

Treebox_info = [0,0]
Log_indexlist = list()

std_indexlist = list()
std_Treebox_info = [0,0]
std_selected_info = []
std_selected_index = int()

stdadd_gender = None

_path = "" # 폴더 경로 입력
img_format = [
    "png","PNG","jpg","JPG","jpeg"
]

def path(inputs): return str(_path + inputs)

BS = 16
pad = (lambda sps: ) # 보안상의 이유로 블라인드 처리됨
unpad = (lambda sps:) # 보안상의 이유로 블라인드 처리됨


class _Encrypt(object):
    '''
    데이터 암호화를 위한 클래스입니다.
    '''
    def __init__(self, key):self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, message):
        message = message.encode()
        raw = pad(message)
        cipher = AES.new(self.key, AES.MODE_CBC, self.__iv().encode('utf8'))
        enc = cipher.encrypt(raw)
        return base64.b64encode(enc).decode('utf-8')

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        cipher = AES.new(self.key, AES.MODE_CBC, self.__iv().encode('utf8'))
        dec = cipher.decrypt(enc)
        return unpad(dec).decode('utf-8')

    def __iv(self):return chr(0) * 16
    
Encrypt = _Encrypt(ENCRYPT_KEY)
# 사용법
# Encrypt.encrypt(original text) -> 암호화
# Encrypt.decrypt(encrypted text) -> 복호화

class ini:
    def initing():
        config = cp.ConfigParser()

        config['dat'] = {}
        config['dat']['누적수익'] = "0"
        config['dat']['누적판매'] = "0"
        config['dat']['제품군'] = "문구,간편식,음료,의약,스낵,생필품,전자,미용,이벤트,기타"
        return config
    def store(config):
        with open("./sources/datas.ini",'w',encoding='UTF-8') as cf:
            config.write(cf)
    def read():
        config = cp.ConfigParser()
        config.read("./sources/datas.ini",encoding = 'UTF-8')
        return config

class datas:
    def init():
        '''
        데이터를 사용하기 위한 초기세팅입니다. 비밀번호,상품데이터,학생데이터,로그데이터,설정데이터 등을 포함합니다.
        '''
        datas.import_pwd()
        datas.pd.LoadData()
        datas.log.LoadData()
        datas.std.LoadData()
        datas.std.Load_balance()
        datas.warn.synchronization()
        datas.warn.Load_warnings()
        datas.stock.LoadData()
    def import_pwd():
        '''
        저장되어있는 비밀번호를 불러옵니다.
        '''
        global pwd
        file = open(path("sources/secure.dat"), 'r')
        pwd = Encrypt.decrypt(file.readline()).split("=")[1]
        file.close()
    class pd:
        '''
        상품목록 데이터 관리에 관한 명령어의 모음입니다.
        '''
        header = ['번호','상품명','이미지','가격','재고','누적판매','제품군']

        def initialize():
            '''
            상품목록 데이터를 초기화하는 함수입니다.
            '''
            f = open(path("sources/datas/상품목록.csv"),'w',newline='')
            rdr = csv.writer(f)
            rdr.writerow(datas.pd.header)
            f.close()
        def LoadData():
            '''
            상품목록 데이터를 불러옵니다.
            '''
            global ProductList
            for _key in datas.pd.header:
                ProductList[_key] = list()
            f = open(path("sources/datas/상품목록.csv"),'r')
            rdr = csv.reader(f)
            for row in rdr:
                for i in range(len(datas.pd.header)):
                    ProductList[datas.pd.header[i]].append(row[i])
            datas.pd.datalen_update()
        def datalen_update() : 
            '''
            상품목록 데이터의 길이를 업데이트합니다. 해당 길이는 헤더가 포함되어있는
            길이 이므로 -1을 해야 실제 데이터의 개수를 구할 수 있습니다.
            '''
            global PDdataLen 
            PDdataLen = len(ProductList[datas.pd.header[0]])
        def add(line):
            '''
            상품목록 데이터를 추가합니다. 

            ['번호','상품명','이미지','가격','재고','누적판매'] 의 포맷으로 리스트를 입력받습니다. 

            line : list()
            '''
            f = open(path('sources/datas/상품목록.csv'),'a', newline='')
            wr = csv.writer(f)
            wr.writerow(line)
            f.close()
        def remove(index_list):
            '''
            입력받은 인덱스에 해당하는 데이터를 모두 삭제합니다.

            ex) index_list = [1,2,3,4] 이면 1,2,3,4번 데이터에 해당하는 데이터들이 삭제됩니다.
            
            index_list : list()
            '''
            global ProductList
            index_list = list(map(int,index_list))
            data = list()
            line = list()
            for i in range(len(ProductList[datas.pd.header[0]])):
                if not (i in index_list):
                    for inds in datas.pd.header:
                        line.append(ProductList[inds][i])
                    data.append(line)
                    line = list()
            f = open(path("sources/datas/상품목록.csv"),'w',newline='')
            rd = csv.writer(f)
            rd.writerows(data)
            f.close()
        def modify(index,header,value):
            '''
            인덱스 리스트에 있는 값 중 헤더값에 해당하는 것의 데이터를 value로 설정합니다.

            index : list()

            header : str()

            value : str() , int() , float()...
            '''
            global ProductList
            value = str(value)
            for idx in index:
                ProductList[header][idx] = value
            datas.pd.save()
        def save():
            '''
            프로그램 내부 변수 ProductList에 저장되어있는 값들을 상품목록 데이터 파일에 덮어 씌웁니다.
            '''
            data = list()
            line = list()
            for i in range(len(ProductList[datas.pd.header[0]])):
                for inds in datas.pd.header:
                    line.append(ProductList[inds][i])
                data.append(line)
                line = list()
            f = open(path("sources/datas/상품목록.csv"),'w',newline='')
            rd = csv.writer(f)
            rd.writerows(data)
            f.close()
        def search(header,value):
            '''
            헤더에 value에 해당하는 값을 가지고있는 모든 index를 리스트형태로 출력합니다. 

            header : str()

            value : str() , int() , float()...

            output -> list()
            '''
            value = str(value)
            index_list = list()
            for i in range(len(ProductList[header])):
                if ProductList[header][i] == value:
                    index_list.append(i)
            return index_list
        def _search(info):
            '''
            입력값에 해당하는 데이터를 모두 가지고있는 데이터의 인덱스를 출력합니다.

            info : list()

            output -> int()
            '''
            dts = list()
            lns = list()
            for i in range(len(ProductList[datas.pd.header[0]])):
                for ins in datas.pd.header:
                    lns.append(ProductList[ins][i])
                dts.append(lns)
                lns = list()
            index = int(dts.index(info))
            return index
        def search_index(index_list):
            '''
            index_list에 해당하는 인덱스의 전체 데이터를 

            ['번호','상품명','이미지','가격','재고','누적판매'] 형태의 데이터의 리스트로 출력합니다.

            index_list : list()

            output -> list(list())
            '''
            data = list()
            lst = list()
            for i in index_list:
                for lsd in datas.pd.header:
                    lst.append(ProductList[lsd][i])
                data.append(lst)
                lst = list()
            return data     
    class log:
        '''
        로그목록 데이터 관리에 관한 명령어의 모음입니다.
        '''
        header = ['년','월','일','시','분','초','생년월일','학번','이름','행동','제품','수','잔액','비고']

        def initialize():
            '''
            로그목록 데이터를 초기화하는 함수입니다.
            '''
            f = open(path("sources/datas/사용로그.csv"),'w',newline='')
            rdr = csv.writer(f)
            rdr.writerow(datas.log.header)
            f.close()
        def LoadData():
            '''
            로그목록 데이터를 불러옵니다.
            '''
            global UsingLog
            for _key in datas.log.header:
                UsingLog[_key] = list()
            f = open(path("sources/datas/사용로그.csv"),'r')
            rdr = csv.reader(f)
            for row in rdr:
                for i in range(len(datas.log.header)):
                    UsingLog[datas.log.header[i]].append(row[i])
        def datalen_update() : 
            '''
            로그목록 데이터의 길이를 업데이트합니다. 해당 길이는 헤더가 포함되어있는
            길이 이므로 -1을 해야 실제 데이터의 개수를 구할 수 있습니다.
            '''
            global LogdataLen
            LogdataLen = len(ProductList[datas.log.header[0]])
        def add(line):
            '''
            로그목록 데이터를 추가합니다. 

            ['년','월','일','시','분','초','생년월일','학번','이름','행동','제품','수','잔액','비고'] 의 포맷으로 리스트를 입력받습니다. 

            line : list()
            '''
            f = open(path('sources/datas/사용로그.csv'),'a', newline='')
            wr = csv.writer(f)
            wr.writerow(line)
            f.close()
        def remove(index_list):
            '''
            입력받은 인덱스에 해당하는 데이터를 모두 삭제합니다.

            ex) index_list = [1,2,3,4] 이면 1,2,3,4번 데이터에 해당하는 데이터들이 삭제됩니다.
            
            index_list : list()
            '''
            global UsingLog
            index_list = list(map(int,index_list))
            data = list()
            line = list()
            for i in range(len(UsingLog[datas.log.header[0]])):
                if not (i in index_list):
                    for inds in datas.log.header:
                        line.append(UsingLog[inds][i])
                    data.append(line)
                    line = list()
            f = open(path("sources/datas/사용로그.csv"),'w',newline='')
            rd = csv.writer(f)
            rd.writerows(data)
            f.close()
        def modify(index,header,value):
            '''
            인덱스 리스트에 있는 값 중 헤더값에 해당하는 것의 데이터를 value로 설정합니다.

            index : list()

            header : str()

            value : str() , int() , float()...
            '''
            global UsingLog
            value = str(value)
            i = 0
            for idx in index:
                UsingLog[header][idx] = value[i]
                i+=1
            datas.log.save()
        def save():
            '''
            프로그램 내부 변수 UsingLog에 저장되어있는 값들을 상품목록 데이터 파일에 덮어 씌웁니다.
            '''
            data = list()
            line = list()
            for i in range(len(UsingLog[datas.log.header[0]])):
                for inds in datas.log.header:
                    line.append(UsingLog[inds][i])
                data.append(line)
                line = list()
            f = open(path("sources/datas/사용로그.csv"),'w',newline='')
            rd = csv.writer(f)
            rd.writerows(data)
            f.close()
        def search(index,value):
            '''
            헤더에 value에 해당하는 값을 가지고있는 모든 index를 리스트형태로 출력합니다. 

            header : str()

            value : str() , int() , float()...

            output -> list()
            '''
            value = str(value)
            index_list = list()
            for i in range(len(UsingLog[index])):
                if UsingLog[index][i] == value:
                    index_list.append(i)
            return index_list
        def search_index(index_list):
            '''
            index_list에 해당하는 인덱스의 전체 데이터를 

            ['년','월','일','시','분','초','생년월일','학번','이름','행동','제품','수','잔액','비고']
             
            형태의 데이터의 리스트로 출력합니다.

            index_list : list()

            output -> list(list())
            '''
            data = list()
            lst = list()
            for i in index_list:
                for lsd in datas.log.header:
                    lst.append(UsingLog[lsd][i])
                data.append(lst)
                lst = list()
            return data
        def current_time():
            time = datetime.datetime.now()
            year = time.year
            month = time.month
            day = time.day
            hour = time.hour
            min = time.minute
            sec = time.second
            reTime = [year,month,day,hour,min,sec]
            return reTime
        def save_log(mod,student,item,value):
            global std_balances
            run = True
            student_num = student[0]
            student_name = student[1]
            time = datas.log.current_time()
            datas.std.LoadData()
            datas.std.Load_balance()
            hd = datas.std.header # ['생년월일','학번','이름','중복번호','성별','경고','포인트','사용합계','충전합계']
            lst_1 = datas.std.search(hd[1],student_num)
            lst_2 = datas.std.search(hd[2],student_name)

            ts = 0
            std = int()
            for i in lst_1:
                for j in lst_2:
                    if i==j:
                        ts += 1
                        std = i
            if ts > 1:
                tkinter.messagebox.showwarning("학생 데이터 오류","검색된 학생 데이터 중 중복되는 데이터가 존재합니다. 학생 데이터의 수정이 필요합니다.")
                run = False
            elif ts == 0:
                tkinter.messagebox.showwarning("존재하지 않는 데이터","해당 학번과 이름은 리스트에 존재하지 않습니다. 입력한 학번 이름이 올바른가 또는 데이터 상에 등록을 해두었는가를 확인해주세요.")
                run = False
            else : std_info = datas.std.search_index([std])
            
            if run:
                if mod == "b": # buy
                    pass
                elif mod == "w": # warning
                    pass
                elif mod == "ia": # item add
                    pass
                elif mod == "id": # item delete
                    pass
                elif mod == "im": # item modify
                    pass
                elif mod == "dp": # deposit
                    pass
                elif mod == "wd": # withdraw
                    pass
            else:pass
    class std:
        '''
        학생목록 데이터 관리에 관한 명령어의 모음입니다.
        '''
        header = ['생년월일','학번','이름','중복번호','성별','경고','포인트','사용합계','충전합계']

        def initialize():
            '''
            학생목록 데이터를 초기화하는 함수입니다.
            '''
            f = open(path("sources/datas/학생목록.csv"),'w',newline='')
            rdr = csv.writer(f)
            rdr.writerow(datas.std.header)
            f.close()
        def LoadData():
            '''
            학생목록 데이터를 불러옵니다.
            '''
            global StudentList
            for _key in datas.std.header:
                StudentList[_key] = list()
            f = open(path("sources/datas/학생목록.csv"),'r')
            rdr = csv.reader(f)
            for row in rdr:
                for i in range(len(datas.std.header)):
                    StudentList[datas.std.header[i]].append(row[i])
            datas.std.datalen_update()
        def datalen_update() : 
            '''
            학생목록 데이터의 길이를 업데이트합니다. 해당 길이는 헤더가 포함되어있는
            길이 이므로 -1을 해야 실제 데이터의 개수를 구할 수 있습니다.
            '''
            global STdataLen
            STdataLen = len(StudentList[datas.std.header[0]])
        def add(line):
            '''
            학생목록 데이터를 추가합니다. 

            ['생년월일','학번','이름','중복번호','성별','경고','포인트','사용합계','충전합계'] 의 포맷으로 리스트를 입력받습니다. 

            line : list()
            '''
            f = open(path('sources/datas/학생목록.csv'),'a', newline='')
            wr = csv.writer(f)
            wr.writerow(line)
            f.close()
        def remove(index_list):
            '''
            입력받은 인덱스에 해당하는 데이터를 모두 삭제합니다.

            ex) index_list = [1,2,3,4] 이면 1,2,3,4번 데이터에 해당하는 데이터들이 삭제됩니다.
            
            index_list : list()
            '''
            global StudentList
            index_list = list(map(int,index_list))
            data = list()
            line = list()
            for i in range(len(StudentList[datas.std.header[0]])):
                if not (i in index_list):
                    for inds in datas.std.header:
                        line.append(StudentList[inds][i])
                    data.append(line)
                    line = list()
            f = open(path("sources/datas/학생목록.csv"),'w',newline='')
            rd = csv.writer(f)
            rd.writerows(data)
            f.close()
        def modify(index,header,value):
            '''
            인덱스 리스트에 있는 값 중 헤더값에 해당하는 것의 데이터를 value로 설정합니다.

            index : list()

            header : str()

            value : str() , int() , float()...
            '''
            global StudentList
            value = str(value)
            for idx in index:
                StudentList[header][idx] = value
            datas.std.save()
        def save():
            '''
            프로그램 내부 변수 Student에 저장되어있는 값들을 상품목록 데이터 파일에 덮어 씌웁니다.
            '''
            data = list()
            line = list()
            for i in range(len(StudentList[datas.std.header[0]])):
                for inds in datas.std.header:
                    line.append(StudentList[inds][i])
                data.append(line)
                line = list()
            f = open(path("sources/datas/학생목록.csv"),'w',newline='')
            rd = csv.writer(f)
            rd.writerows(data)
            f.close()
        def save_balance(_index,bal):
            global StudentList
            datas.std.LoadData()
            info = datas.std.search_index([_index])[0]
            PRE_Enc_key = info[2]
            pre_enc = _Encrypt(PRE_Enc_key)
            
            _Enc_key = pre_enc.encrypt(info[0])
            _enc = _Encrypt(_Enc_key)

            bal = _enc.encrypt(str(bal))
            
            StudentList[datas.std.header[6]][_index] = bal
            datas.std.save()
        def Load_balance():
            global std_balances
            datas.std.LoadData()
            std_balances = list()
            for idx in range(len(StudentList[datas.std.header[0]])-1):
                info = datas.std.search_index([idx+1])[0]

                encrypted_bal = info[6]

                PRE_Enc_key = info[2]
                pre_enc = _Encrypt(PRE_Enc_key)

                _Enc_key = pre_enc.encrypt(info[0])
                _enc = _Encrypt(_Enc_key)

                bal = _enc.decrypt(encrypted_bal)
                std_balances.append(bal)
        def search(header,value):
            '''
            헤더에 value에 해당하는 값을 가지고있는 모든 index를 리스트형태로 출력합니다. 

            header : str()

            value : str() , int() , float()...

            output -> list()
            '''
            value = str(value)
            index_list = list()
            for i in range(len (StudentList[header])):
                if StudentList[header][i] == value:
                    index_list.append(i)
            return index_list
        def _search(info):
            '''
            입력값에 해당하는 데이터를 모두 가지고있는 데이터의 인덱스를 출력합니다.

            info : list()

            output -> int()
            '''
            dts = list()
            lns = list()
            for i in range(len(StudentList[datas.std.header[0]])):
                for ins in datas.std.header:
                    lns.append(StudentList[ins][i])
                dts.append(lns)
                lns = list()
            index = int(dts.index(info))
            return index
        def search_index(index_list):
            '''
            index_list에 해당하는 인덱스의 전체 데이터를 

            ['생년월일','학번','이름','중복번호','성별','경고','포인트','사용합계','충전합계'] 형태의 데이터의 리스트로 출력합니다.

            index_list : list()

            output -> list(list())
            '''
            data = list()
            lst = list()
            for i in index_list:
                for lsd in datas.std.header:
                    lst.append(StudentList[lsd][i])
                data.append(lst)
                lst = list()
            return data     
    class warn:
        header = ['생년월일','학번','이름','중복번호','성별','경고','경고사유']
        def initialize():
            '''
            걍고목록 데이터를 초기화하는 함수입니다.
            '''
            f = open(path("sources/datas/학생목록.csv"),'w',newline='')
            rdr = csv.writer(f)
            rdr.writerow(datas.warn.header)
            f.close()
        def LoadData():
            '''
            경고목록 데이터를 불러옵니다.
            '''
            global WarningList
            for _key in datas.warn.header:
                WarningList[_key] = list()
            f = open(path("sources/datas/경고목록.csv"),'r')
            rdr = csv.reader(f)
            for row in rdr:
                for i in range(len(datas.warn.header)):
                    WarningList[datas.warn.header[i]].append(row[i])
        def synchronization():
            global WarningList
            datas.std.LoadData()
            datas.warn.LoadData()
            warn_len = len(WarningList[datas.warn.header[0]])-1
            std_len = len(StudentList[datas.std.header[0]])-1
            if warn_len != std_len:
                dcs = std_len - warn_len
                _index = warn_len
                for i in range(dcs):
                    i += 1
                    index = _index + i
                    _info = datas.std.search_index([index])[0][0:6]
                    _info.append("-/-/-")
                    datas.warn.add(_info)
        def add(line):
            '''
            경고목록 데이터를 추가합니다. 

            ['생년월일','학번','이름','중복번호','성별','경고사유'] 의 포맷으로 리스트를 입력받습니다. 

            line : list()
            '''
            f = open(path('sources/datas/경고목록.csv'),'a', newline='')
            wr = csv.writer(f)
            wr.writerow(line)
            f.close()     
        def save():
            '''
            프로그램 내부 변수 WarningList에 저장되어있는 값들을 상품목록 데이터 파일에 덮어 씌웁니다.
            '''
            data = list()
            line = list()
            for i in range(len(WarningList[datas.warn.header[0]])):
                for inds in datas.warn.header:
                    line.append(WarningList[inds][i])
                data.append(line)
                line = list()
            f = open(path("sources/datas/경고목록.csv"),'w',newline='')
            rd = csv.writer(f)
            rd.writerows(data)
            f.close()
        def Load_warnings():
            '''
            index : 학생1,학생2,학생3 ... 
                    0,1,2
            '''
            global _Warnings
            datas.warn.LoadData()
            Wlst = WarningList[datas.warn.header[6]]
            for i in range(1,len(Wlst)):
                Wlst[i] = Wlst[i].split("/")
            _Warnings = Wlst
        def add_warning(index,Warn):
            global StudentList,_Warnings,WarningList
            Wths = int(WarningList[datas.warn.header[5]][index])
            if Wths >= 3:
                tkinter.messagebox.showerror("경고 최대 한도 초과","해당 학생은 경고의 최대 한도를 초과하였습니다. 따라서 경고 횟수는 증가하나 사유는 1번 경고에 저장됩니다.")
                WarningList[datas.warn.header[5]][index] = str(int(WarningList[datas.warn.header[5]][index])+1)
                StudentList[datas.std.header[5]][index] = str(int(StudentList[datas.std.header[5]][index])+1)
                _Warnings[index][0] = Warn
            else:
                _Warnings[index][Wths] = Warn
                WarningList[datas.warn.header[5]][index] = str(int(WarningList[datas.warn.header[5]][index])+1)
                StudentList[datas.std.header[5]][index] = str(int(StudentList[datas.std.header[5]][index])+1)
            _ks = ["경고사유"]
            for i in range(1,len(_Warnings)):
                ks = str(_Warnings[i][0]) +"/"+ str(_Warnings[i][1]) +"/"+ str(_Warnings[i][2])
                _ks.append(str(ks))
            WarningList[datas.warn.header[6]] = _ks
            datas.warn.save()
            datas.std.save()
        def del_warning(index):
            global StudentList,_Warnings,WarningList
            Wths = int(WarningList[datas.warn.header[5]][index])
            if Wths > 3: Wths = 3; de = False
            else : de = True
            if Wths >0:
                WarningList[datas.warn.header[5]][index] = str(int(WarningList[datas.warn.header[5]][index])-1)
                StudentList[datas.std.header[5]][index] = str(int(StudentList[datas.std.header[5]][index])-1)
                if de:_Warnings[index][Wths-1] = '-'
                _ks = ["경고사유"]
                for i in range(1,len(_Warnings)):
                    ks = str(_Warnings[i][0]) +"/"+ str(_Warnings[i][1]) +"/"+ str(_Warnings[i][2])
                    _ks.append(str(ks))
                WarningList[datas.warn.header[6]] = _ks
                datas.warn.save()
                datas.std.save()
            else:
                tkinter.messagebox.showerror("제거할 경고가 없음","현재 경고횟수가 0회이므로 차감할 경고가 없습니다.")
    class stock:
        '''
        재고 관리 데이터 관리에 관한 명령어의 모음입니다.
        '''
        header = ['날짜','제품군','제품명','입고/출고','개수','수익']

        def initialize():
            '''
            학생목록 데이터를 초기화하는 함수입니다.
            '''
            f = open(path("sources/datas/재고관리.csv"),'w',newline='')
            rdr = csv.writer(f)
            rdr.writerow(datas.stock.header)
            f.close()
        def LoadData():
            '''
            학생목록 데이터를 불러옵니다.
            '''
            global stockLogList
            for _key in datas.stock.header:
                stockLogList[_key] = list()
            f = open(path("sources/datas/재고관리.csv"),'r')
            rdr = csv.reader(f)
            for row in rdr:
                for i in range(len(datas.stock.header)):
                    stockLogList[datas.stock.header[i]].append(row[i])
        def add(line):
            '''
            재고 관리 데이터를 추가합니다. 

            ['날짜','제품군','제품명','입고/출고','개수'] 의 포맷으로 리스트를 입력받습니다. 

            line : list()
            '''
            f = open(path('sources/datas/재고관리.csv'),'a', newline='')
            wr = csv.writer(f)
            wr.writerow(line)
            f.close()
        def remove(index_list):
            '''
            입력받은 인덱스에 해당하는 데이터를 모두 삭제합니다.

            ex) index_list = [1,2,3,4] 이면 1,2,3,4번 데이터에 해당하는 데이터들이 삭제됩니다.
            
            index_list : list()
            '''
            global stockLogList
            index_list = list(map(int,index_list))
            data = list()
            line = list()
            for i in range(len(stockLogList[datas.stock.header[0]])):
                if not (i in index_list):
                    for inds in datas.stock.header:
                        line.append(stockLogList[inds][i])
                    data.append(line)
                    line = list()
            f = open(path("sources/datas/재고관리.csv"),'w',newline='')
            rd = csv.writer(f)
            rd.writerows(data)
            f.close()
        def modify(index,header,value):
            '''
            인덱스 리스트에 있는 값 중 헤더값에 해당하는 것의 데이터를 value로 설정합니다.

            index : list()

            header : str()

            value : str() , int() , float()...
            '''
            global stockLogList
            value = str(value)
            for idx in index:
                stockLogList[header][idx] = value
            datas.stock.save()
        def save():
            '''
            프로그램 내부 변수 Student에 저장되어있는 값들을 상품목록 데이터 파일에 덮어 씌웁니다.
            '''
            data = list()
            line = list()
            for i in range(len(stockLogList[datas.stock.header[0]])):
                for inds in datas.stock.header:
                    line.append(stockLogList[inds][i])
                data.append(line)
                line = list()
            f = open(path("sources/datas/재고관리.csv"),'w',newline='')
            rd = csv.writer(f)
            rd.writerows(data)
            f.close()
        def search(header,value):
            '''
            헤더에 value에 해당하는 값을 가지고있는 모든 index를 리스트형태로 출력합니다. 

            header : str()

            value : str() , int() , float()...

            output -> list()
            '''
            value = str(value)
            index_list = list()
            for i in range(len (stockLogList[header])):
                if stockLogList[header][i] == value:
                    index_list.append(i)
            return index_list
        def _search(info):
            '''
            입력값에 해당하는 데이터를 모두 가지고있는 데이터의 인덱스를 출력합니다.

            info : list()

            output -> int()
            '''
            dts = list()
            lns = list()
            for i in range(len(stockLogList[datas.stock.header[0]])):
                for ins in datas.stock.header:
                    lns.append(stockLogList[ins][i])
                dts.append(lns)
                lns = list()
            index = int(dts.index(info))
            return index
        def search_index(index_list):
            '''
            index_list에 해당하는 인덱스의 전체 데이터를 

            ['날짜','제품군','제품명','입고/출고','개수'] 형태의 데이터의 리스트로 출력합니다.

            index_list : list()

            output -> list(list())
            '''
            data = list()
            lst = list()
            for i in index_list:
                for lsd in datas.stock.header:
                    lst.append(stockLogList[lsd][i])
                data.append(lst)
                lst = list()
            return data   
        def search_timeline(time1,time2):
            '''
            input) time1 : YYMMDD , time2 : YYMMDD

            output) index_list : list()
            (header included index)
            '''
            time1 = str(time1)
            time2 = str(time2)
            stock_date = list()
            for i in range(len(stockLogList[datas.stock.header[0]])-1):
                dt = datetime.datetime.strptime(stockLogList[datas.stock.header[0]][i+1],'%Y-%m-%d')
                dt = dt.date()
                stock_date.append(dt)
            search_index = list()
            time1 = datetime.datetime.strptime(time1, '%Y%m%d')
            time1 = time1.date()
            time2 = datetime.datetime.strptime(time2, '%Y%m%d')
            time2 = time2.date()
            tmax = 0
            tmin = 0
            td_test = (time1 - time2).total_seconds()
            if td_test >= 0:
                tmax = time1
                tmin = time2
            else:
                tmax = time2
                tmin = time1
            for i in range(len(stock_date)):
                max_time_sub = tmax - stock_date[i]
                min_time_sub = stock_date[i] - tmin
                max_time_sub = max_time_sub.total_seconds()
                min_time_sub = min_time_sub.total_seconds()
                if max_time_sub >=0 and min_time_sub >= 0: search_index.append(i+1)
            return search_index
            
            
class fnc:
    def Null() : 
        '''
        비어있는 함수입니다. 버튼 커맨드 초기화에 쓰입니다.
        '''
        pass
    def img(path_,root): 
        '''
        이미지를 ImageTk의 PhotoImage 형태로 불러와 스크린에서 사용합니다.

        path : str()

        root : Tkinter screen
        '''
        
        return ImageTk.PhotoImage(Image.open(path(path_)),master=root)
    def exit_command():
        '''
        프로그램 종료 시 나타나는 메시지박스입니다.
        '''
        msgbox = tkinter.messagebox.askyesno('종료하시겠습니까?','프로그램을 종료하시겠습니까?')
        if msgbox:
            global exit
            exit = True
            sys.exit()
    def main_pwdTest():
        '''
        메인 스크린에서의 비밀번호 입력검사 함수
        '''
        pw_input = pwE.get()
        if fnc.pwd_test(pw_input):fnc.pw_main_transition()
        else : pass
        pwE.delete(0, len(pw_input))
    def pwd_test(input):
        '''
        입력한 비밀번호가 옳은 비밀번호인지 검사합니다.
        '''
        pw_input = input
        if pw_input == pwd:return True
        elif pw_input == Encrypt.decrypt(backup_key2):return True
        else:msgbox = tkinter.messagebox.showwarning("비밀번호 오류","잘못된 비밀번호를 입력하셨습니다. 다시 입력해주세요.");return False
    def logout():
        '''
        로그아웃 버튼 명령어입니다. 메인-메인 -> 메인-비번 으로 넘어갑니다.
        '''
        msgbox = tkinter.messagebox.askyesno('로그아웃 확인','로그아웃 하시겠습니까?')
        if msgbox : fnc.main_pw_transition()
    def change_password():
        '''
        비밀번호 변경을 위한 함수입니다.
        '''
        global existpw,newpw,repw,proot,pwd
        pst_pw = existpw.get()
        new_pw = newpw.get()
        reco_pw = repw.get()

        if pst_pw == pwd or pst_pw == Encrypt.decrypt(backup_key):
            if new_pw == reco_pw:
                if new_pw != "":
                    pwd = new_pw
                    _pwd = "password="+pwd
                    f = open(path("sources/secure.dat"),'w')
                    enc_newpw = Encrypt.encrypt(_pwd)
                    f.writelines(enc_newpw)
                    f.close()
                    msgbox = tkinter.messagebox.showinfo("비밀번호 변경완료","비밀번호 변경이 완료되었습니다.")
                    proot.destroy()
                else:msgbox = tkinter.messagebox.showwarning("일치하지 않는 비밀번호","재입력한 비밀번호와 새로운 비밀번호가 일치하지 않습니다. 다시 입력해주세요.")

            else : 
                msgbox = tkinter.messagebox.showwarning("일치하지 않는 비밀번호","재입력한 비밀번호와 새로운 비밀번호가 일치하지 않습니다. 다시 입력해주세요.")
                newpw.delete(0,len(new_pw))
                repw.delete(0,len(reco_pw))
        else:
            msgbox = tkinter.messagebox.showwarning("일치하지 않는 비밀번호","비밀번호가 일치하지 않습니다. 다시 입력해주세요. \n\n만약 비밀번호를 잊어버린 경우 관리자에게 도움을 요청하세요.")
            existpw.delete(0,len(pst_pw))
        proot.lift()
        proot.update()
    def pd_lists_update():
        '''
        상품관리 화면에서 나타나는 리스트를 데이터로부터 불러와 pd_btn_list 에 버튼에 관한 데이터를 저장합니다.
        '''
        global pd_btn_list,root,pd_page_max
        datas.pd.LoadData()
        _list = ProductList["상품명"][1:]
        pd_page_max = int(len(_list))//10 + 1
        i = 1
        for ins in _list:
            pd_btn_list[ins] = windows.pd_management._btn(i)
            fnc.List_Imaging(pd_btn_list[ins].info)
            try:
                pd_btn_list[ins].img = fnc.img("./sources/imgs/lists/pdm/"+pd_btn_list[ins].info[0][1]+".png",root=root)
                pd_btn_list[ins].btn["image"] = pd_btn_list[ins].img
            finally:
                i+=1
        root.update()
    def pd_paging():
        '''
        pd_btn_list에 저장되어있는 버튼을 규칙에 맞게 배치합니다.
        '''
        global root,pd_btn_list
        _list = ProductList["상품명"][1:]
        for ins in _list:
            dt = pd_btn_list[ins]
            if pd_page == dt.page:
                pd_btn_list[ins].btn.place(x=dt.x,y=dt.y)
        root.update()
    def List_Imaging(info):
        '''
        정해진 규칙대로 버튼에 들어갈 이미지를 자동으로 생성-저장합니다. 

        해당 버튼에 대한 정보가 입력되면 내부 알고리즘에 의해 이미지가 생성되어 sources/imgs/lists/pdm/ 이하에 저장됩니다.

        info : list() ... ['번호','상품명','이미지','가격','재고','누적판매']
        '''
        def loadfont(fontsize):
            ttf = path('sources/font.ttf')
            return ImageFont.truetype(font=ttf, size=fontsize)
        Font = loadfont(50)
        info = info[0]
        file_name = info[2]
        _file_name = info[1] + ".png"

        template = Image.open(path("sources/imgs/lists/template.png"))
        List_img = Image.new("RGB",(750,150))
        List_img.paste(template)

        try : 
            product = Image.open("./상품 이미지/"+file_name)
            product = product.resize((100,100))
            List_img.paste(product,(28,22))
        except : pass

        title = info[1]
        price = info[3]

        List_text = ImageDraw.Draw(List_img)
        List_text.text(xy=(135,60), text=title, fill=(0, 0, 0), font=Font)
        List_text.text(xy=(550,60), text=price, fill=(0, 0, 0), font=Font)

        List_img.save(path("sources/imgs/lists/pdm/"+_file_name))
        fnc.img_100x100()
    def pd_update():
        global root,pd_btn_list
        '''
        상품관리 화면에서 데이터 불러와서 배치하는 과정을 한번에 합니다.
        '''
        try:
            for ins in ProductList["상품명"][1:]:
                pd_btn_list[ins].btn.destroy()
        finally:
            pd_btn_list = dict()
            fnc.pd_lists_update()
            fnc.pd_paging()
            root.update()
            root.update()
    def pg_up():
        '''
        오른쪽 화살표(페이지 업) 기능입니다
        '''
        global pd_page,page
        if pd_page < pd_page_max:
            pd_page += 1
            page["text"] = "페이지  [{}/{}]".format(pd_page,pd_page_max)
            fnc.pd_update()
    def pg_down():
        '''
        왼쪽 화살표(페이지 옆으로) 기능입니다
        '''
        global pd_page,page
        if pd_page  > 1:
            pd_page -= 1
            page["text"] = "페이지  [{}/{}]".format(pd_page,pd_page_max)
            fnc.pd_update()
    def pd_open_info(_info):
        '''
        상품 클릭 시 나타나는 정보를 출력하는 기능입니다.
        '''
        info = _info[0]
        global info_L,pd_selected,root
        info_L["text"] = "상품군 : {}\n상품명 : {}\n가격 : {}원\n재고 : {}   \n   누적판매 : {}".format(info[6],info[1],info[3],info[4],info[5])
        pd_selected = info
        root.update()
    def pd_remove():
        '''
        상품관리 탭의 추가버튼 팝업의 제거 기능입니다
        '''
        global info_L,pd_selected,root
        msgbox = tkinter.messagebox.askyesno('제거 여부',pd_selected[1]+'의 데이터를 제거하시겠습니까?')
        if msgbox:
            idx = datas.pd._search(pd_selected)
            datas.pd.remove([idx])
            dt = pd_selected
            pd_selected = list()
            info_L["text"] = "상품군 : -\n상품명 : -\n가격 : -\n재고 : -   \n   누적판매 : -"
            fnc.pd_update()
            root.update()
            msgbox = tkinter.messagebox.showinfo("제거완료",dt[1]+"의 데이터가 삭제되었습니다.")
    def pd_imgDir():
        '''
        상품관리의 추가 팝업의 이미지찾기 기능입니다.
        '''
        global _pdimg,pdimgBt,addroot,_pdaddimg
        __path = "./상품 이미지/"
        img_file = filedialog.askopenfilename(initialdir="/",\
                 title = "파일을 선택 해 주세요",\
                    filetypes=(("png","*.png"),("jpg","*.jpg"),("all files","*.*")))
        img_name = img_file.split("/")[-1]
        addroot.lift()
        
        if img_file != "":
            if not (img_name.split(".")[-1] in img_format) : 
                messagebox = tkinter.messagebox.showerror("파일 형식 오류","지원하지 않는 파일형식입니다. 다시 선택하세요.\n\n지원파일형식:png,PNG,jpg,JPG,jpeg")
                fnc.pd_imgDir()
            else:
                if not img_name in os.listdir(__path):
                    shutil.copyfile(img_file,__path+img_name)
                
                _pdaddimg = img_name
                _pdimg= Image.open(__path + img_name)
                _pdimg = _pdimg.resize((100,100))
                _pdimg = ImageTk.PhotoImage(_pdimg)

                pdimgBt["image"] = _pdimg
                addroot.update()
        else:
            _pdaddimg = "."
    def pdAdd():
        '''
        상품관리 탭의 추가 버튼 기능입니다.
        '''
        global addroot,pdpwd,pdstock,pdprice,_pdaddimg,pdcombobox
        if _pdaddimg == "":_pdaddimg = "-"
        fls = True
        _pdname = pdName.get()
        _pdstock = pdstock.get()
        _pdnum = pdprice.get()
        _pdpw = pdpwd.get()
        try: _pdstock = int(_pdstock)
        except :pdstock.delete(0, len(str(_pdstock))); messagebox = tkinter.messagebox.showerror("올바르지 않은 입력","재고가 올바르지 않습니다. 0이상의 정수 범위 내에서 재고를 입력해주십시오.") ; fls = False ; addroot.lift()
        if _pdstock < 0: pdstock.delete(0, len(str(_pdstock)));messagebox = tkinter.messagebox.showerror("올바르지 않은 입력","재고가 올바르지 않습니다. 0이상의 정수 범위 내에서 재고를 입력해주십시오.") ; fle = False ; addroot.lift()

        try:_pdnum = int(_pdnum)
        except : pdprice.delete(0, len(str(_pdnum)));tkinter.messagebox.showerror("올바르지 않은 입력","입력된 가격이 올바르지 않습니다. 가격은 0이상의 정수 범위내에서 입력해주십시오.") ; fls = False ; addroot.lift()
        if _pdnum>999999:pdprice.delete(0, len(str(_pdnum)));tkinter.messagebox.showerror("올바르지 않은 가격","가격의 최대치를 넘어섰습니다. 가격의 범위는 최대 99만9999원입니다. 다시 입력해주십시오.") ; fls = False ; addroot.lift()
        elif _pdnum<0:pdprice.delete(0, len(str(_pdnum)));tkinter.messagebox.showerror("올바르지 않은 가격","가격은 음수가 될 수 없습니다. 다시 입력해주십시오.") ; fls = False ; addroot.lift()
        elif not pdcombobox.get() in ini.read()["dat"]["제품군"].split(",") : pdcombobox.set("");tkinter.messagebox.showerror("제품군 미선택","설정된 제품군이 올바르지 않습니다. 제품군 선택 후 다시 시도해주세요.") ; fls = False; addroot.lift()

        if len(str(_pdname)) >= 10: tkinter.messagebox.showerror("올바르지 않은 입력","상품명이 너무 깁니다. 9글자 이내로 입력해주십시오.") ; fls = False ; addroot.lift()

        if not fnc.pwd_test(_pdpw) : pdpwd.delete(0, len(str(_pdpw))) ; fls = False ; addroot.lift()

        if fls:
            num = random.randint(0,9999)
            lst = [num,_pdname,_pdaddimg,_pdnum,_pdstock,'0',pdcombobox.get()]
            datas.pd.add(lst)
            _pdaddimg = str()
            addroot.destroy()
            fnc.pd_update()
            tkinter.messagebox.showinfo("추가 완료",_pdname + "상품이 상품목록 데이터파일에 성공적으로 추가되엇습니다!")
        fnc.img_100x100()
    def img_100x100():
        __path = "./상품 이미지/"
        __path2 = "./sources/imgs/100x100/"
        files = os.listdir(__path)
        x100 = os.listdir(__path2)
        for img in files:
            if not img in x100:
                _img= Image.open(__path + img)
                _img = _img.resize((100,100))

                x100_img = Image.new("RGB",(100,100))
                x100_img.paste(_img,(0,0))
                x100_img.save(__path2 + img)
    def on_pd_mdfy():
        if pd_selected != list():
            windows.pd_management.modify()
        else:
            message = tkinter.messagebox.showwarning("선택되지 않은 상품","수정기능을 사용하시려면 상품을 선택해주세요. 선택한 상품은 우측 하단에 표시됩니다.")
    class pd_mdfy:
        def edit(_num):
            global mdfyroot,pdmdfy1Bt,item_name,pdmdfy2Bt,item_price,pdmdfy3Bt,item_stock
            if _num == 0:
                pdmdfy1Bt.destroy()
                item_name.destroy()
                windows.pd_management.mdfy_udc._1t()
            if _num == 1:
                pdmdfy2Bt.destroy()
                item_price.destroy()
                windows.pd_management.mdfy_udc._2t()
            if _num == 2:
                pdmdfy3Bt.destroy()
                item_stock.destroy()
                windows.pd_management.mdfy_udc._3t()
            pd_modify[_num] = True
        def cancel(_num):
            global mdfyroot,pdconfirm1Bt,pdcancel1Bt,_NameEntry,pdconfirm2Bt,pdcancel2Bt,_PriceEntry,pdcancel3Bt,pdminusBt,pdplusBt,pdsetBt,_StockEntry
            if _num == 0:
                pdconfirm1Bt.destroy()
                pdcancel1Bt.destroy()
                _NameEntry.destroy()
                windows.pd_management.mdfy_udc._1f()
            if _num == 1:
                pdconfirm2Bt.destroy()
                pdcancel2Bt.destroy()
                _PriceEntry.destroy()
                windows.pd_management.mdfy_udc._2f()
            if _num == 2:
                pdcancel3Bt.destroy()
                pdminusBt.destroy()
                pdplusBt.destroy()
                pdsetBt.destroy()
                _StockEntry.destroy()
                windows.pd_management.mdfy_udc._3f()
            pd_modify[_num] = False
        def confirm(num):
            global mdfyroot,pd_selected
            if num == 0:
                Name = _NameEntry.get()
                if len(Name) > 9 : 
                    _NameEntry.delete(0,len(str(Name)))
                    _NameEntry.insert(0,pd_selected[1])
                    tkinter.messagebox.showerror("올바르지 않은 입력","상품명이 너무 깁니다. 9글자 이내로 입력해주십시오.")
                else : 
                    pd_selected[1] = Name
                    fnc.pd_mdfy.cancel(0)
            elif num == 1:
                Price = _PriceEntry.get()
                try: Price = int(Price)
                except:
                    _PriceEntry.delete(0,len(str(Price)))
                    _PriceEntry.insert(0,pd_selected[3])
                    tkinter.messagebox.showerror("올바르지 않은 입력","입력된 가격이 올바르지 않습니다. 가격은 0이상의 정수 범위내에서 입력해주십시오.")
                else:
                    if Price<0 :
                        _PriceEntry.delete(0,len(str(Price)))
                        _PriceEntry.insert(0,pd_selected[3])
                        tkinter.messagebox.showerror("올바르지 않은 가격","가격은 음수가 될 수 없습니다. 다시 입력해주십시오.")
                    elif Price>999999:
                        _PriceEntry.delete(0,len(str(Price)))
                        _PriceEntry.insert(0,pd_selected[3])
                        tkinter.messagebox.showerror("올바르지 않은 가격","가격의 최대치를 넘어섰습니다. 가격의 범위는 최대 99만9999원입니다. 다시 입력해주십시오.")
                    else:
                        pd_selected[3] = Price
                        fnc.pd_mdfy.cancel(1)
            else:
                delta = _StockEntry.get()
                Stock = int(pd_selected[4])
                try:delta = int(delta)
                except:
                    _StockEntry.delete(0,len(str(delta)))
                    _StockEntry.insert(0,"0")
                    tkinter.messagebox.showerror("올바르지 않은 입력","재고가 올바르지 않습니다. 0이상의 정수 범위 내에서 재고를 입력해주십시오.")
                else:
                    if num == 2:
                        _stock = Stock - delta
                    elif num == 3:
                        _stock = delta
                    elif num == 4:
                        _stock = Stock + delta
                    pd_selected[4] = _stock
                    fnc.pd_mdfy.cancel(2)
            print(pd_selected)
        def save():
            global mdfyroot,pd_selected,pd_modify
            index = mdfy_index
            n = 0
            pds = pdcomboboxmdfy.get()
            pd_selected[6] = pds
            for ins in datas.pd.header:
                datas.pd.modify([index],ins,pd_selected[n])
                n+=1
            pd_selected = list()
            pd_modify = [False,False,False]
            mdfyroot.destroy()
            fnc.pd_update()
            tkinter.messagebox.showinfo("저장완료","선택한 데이터가 성공적으로 수정되었습니다.")
        def img():
            global mdfyroot,pd_selected,_pdrdimg,pdrdimgBt
            __path = "./상품 이미지/"
            img_file = filedialog.askopenfilename(initialdir="/",\
                 title = "파일을 선택 해 주세요",\
                    filetypes=(("png","*.png"),("jpg","*.jpg"),("all files","*.*")))
            img_name = img_file.split("/")[-1]
            mdfyroot.lift()
            if img_file != "":
                if not (img_name.split(".")[-1] in img_format) : 
                    messagebox = tkinter.messagebox.showerror("파일 형식 오류","지원하지 않는 파일형식입니다. 다시 선택하세요.\n\n지원파일형식:png,PNG,jpg,JPG,jpeg")
                    fnc.pd_imgDir()
                else:
                    if not img_name in os.listdir(__path):
                        shutil.copyfile(img_file,__path+img_name)
                    
                    _img= Image.open(__path + img_name)
                    _img = _img.resize((100,100))
                    _img = ImageTk.PhotoImage(_img)

                    pd_selected[2] = img_name
                    fnc.img_100x100()
                    _pdrdimg= fnc.img("sources/imgs/100x100/"+pd_selected[2],root=mdfyroot)
                    pdrdimgBt["image"] = _pdrdimg
                    mdfyroot.update()
            else:
                mdfyroot.lift()
        def cas():
            global mdfyroot,pd_modify,pd_selected,mdfy_index
            pd_modify = [False,False,False]
            mdfyroot.destroy()
            pd_selected = list()
            mdfy_index = int()
    class log:
        def TreeBox(dat): # ['년','월','일','시','분','초','생년월일','학번','이름','행동','제품','수','잔액','비고']
            global root,treeview
            tasd = True if dat == UsingLog else False

            frame=tkinter.Frame(root)

            _font=Font(family="나눔 고딕", size=25,weight="bold")
            treeview=tkinter.ttk.Treeview(frame,columns=["one", "two","three","four","five","six","seven","eight","nine","ten",'eleven'], displaycolumns=["one", "two","three","four","five","six","seven","eight","nine","ten",'eleven'])
            treeview["height"] = 27
            style = tkinter.ttk.Style()
            style.configure("Treeview.Heading", font=("나눔 고딕", 25))

            verscrlbar = tkinter.ttk.Scrollbar(frame, 
                           orient ="vertical", 
                           command = treeview.yview)
            verscrlbar.pack(side="right", fill="y")
            
            
            treeview.configure(yscrollcommand = verscrlbar.set)

            wd = 153

            treeview.column("#0", width=30,anchor="w")
            treeview.heading("#0", text="",anchor="w")

            treeview.column("one", width=wd, anchor="w")
            treeview.heading("one", text="년", anchor="w")

            treeview.column("two", width=wd, anchor="w")
            treeview.heading("two", text="월.일", anchor="w")

            treeview.column("three", width=wd, anchor="w")
            treeview.heading("three", text="시:분:초", anchor="w")

            treeview.column("four", width=wd, anchor="w")
            treeview.heading("four", text="생년월일", anchor="w")

            treeview.column("five", width=wd, anchor="w")
            treeview.heading("five", text="학번", anchor="w")

            treeview.column("six", width=wd, anchor="w")
            treeview.heading("six", text="이름", anchor="w")

            treeview.column("seven", width=wd, anchor="w")
            treeview.heading("seven", text="행동", anchor="w")

            treeview.column("eight", width=wd, anchor="w")
            treeview.heading("eight", text="제품", anchor="w")

            treeview.column("nine", width=wd, anchor="w")
            treeview.heading("nine", text="개수", anchor="w")

            treeview.column("ten", width=wd, anchor="w")
            treeview.heading("ten", text="잔액", anchor="w")

            treeview.column("eleven", width=wd, anchor="w")
            treeview.heading("eleven", text="비고", anchor="w")

            treelist = fnc.log.Treebox_list(dat)
            for i in range(len(treelist)):
                if tasd: treeview.insert('', 'end', text=str(i+1),values=treelist[i], iid=str(i)+"번")
                else :   treeview.insert('', 'end', text=dat[i],values=treelist[i], iid=str(i)+"번")
                treeview.tag_configure(str(i)+"번" ,font=_font)

            treeview.pack(side="left")
            frame.place(x=100,y=250)

            root.update()
        def Treebox_list(lst):
            global treeview,root
            datas.log.LoadData()
            if lst == UsingLog:
                its = list()
                tsl = list()
                rtn = list()
                for i in range(len(UsingLog[datas.log.header[0]])-1):
                    for inds in datas.log.header:
                        tsl.append(UsingLog[inds][i+1])
                    its.append(tsl)
                    tsl = list()

                for lines in its: #['년','월','일','시','분','초','생년월일','학번','이름','행동','제품','수','잔액','비고']
                    lines[1] = str(lines[1])+'.'+str(lines[2])
                    lines[3] = str(lines[3])+':'+str(lines[4])+':'+str(lines[5])

                    del lines[4:6]
                    del lines[2]
                    
                    rtn.append(tuple(lines))
                return rtn

            else: # [index_list] ex)[1,2,3,4,...]
                datum = datas.log.search_index(lst)
                rtn = list()
                for lines in datum:
                    lines[1] = str(lines[1])+'.'+str(lines[2])
                    lines[3] = str(lines[3])+':'+str(lines[4])+':'+str(lines[5])

                    del lines[4:6]
                    del lines[2]

                    rtn.append(tuple(lines))
                return rtn
        def search():
            global Log_entry,Log_searchSub,root,Log_indexlist,Treebox_info
            datas.log.LoadData()
            _LogEntry = Log_entry.get()
            mode = Log_searchSub.get()
            Log_indexlist = list()
            if not mode in datas.log.header:
                tkinter.messagebox.showwarning("존재하지 않는 헤더값","해당 종류의 목록에서는 검색이 불가합니다. 검색 종류설정을 해주세요")
                Log_searchSub.set("종류선택")
                Treebox_info = []
            else:
                Log_indexlist = datas.log.search(mode,_LogEntry)
                fnc.log.TreeBox(Log_indexlist)
                root.update()
                Treebox_info = [mode,_LogEntry]
        def download():
            if Treebox_info != [] or Treebox_info == [0,0]:
                if Treebox_info == [0,0] : _All = True
                else : _All = False
                msgbox = tkinter.messagebox.askyesno('로그 다운로드','검색된 로그 데이터를 다운로드하시겠습니까?\n\n다운로드 된 로그 데이터는 다운로드 폴더 내에 저장됩니다.')
                if msgbox:
                    datas.log.LoadData()
                    hdr = datas.log.header
                    datum = list()
                    if _All: 
                        lns = list()
                        for i in range(len(UsingLog[datas.log.header[0]])-1):
                            for inds in hdr:
                                lns.append(UsingLog[inds][i+1])
                            datum.append(lns)
                            lns = list()
                    else:datum = datas.log.search_index(Log_indexlist)
                    _LogCsv = list()
                    _LogCsv.append(hdr)
                    for dt in datum:
                        _LogCsv.append(dt)
                    
                    ct = datas.log.current_time()
                    fname = str(ct[0])+str(ct[1])+str(ct[2])+str(ct[3])+str(ct[4])+str(ct[5])+"_로그데이터_"+str(Treebox_info[0])+"_"+str(Treebox_info[1])+".csv"
                    __path = "./다운로드/"+str(fname)

                    with open(__path, 'w', newline='') as file:
                        writer = csv.writer(file)
                        for row in _LogCsv:
                            writer.writerow(row)
                    tkinter.messagebox.showinfo("다운로드완료","{} 위치에 성공적으로 로그 데이터를 저장하였습니다.".format(__path))
    class std:
        def TreeBox(dat): # ['생년월일','학번','이름','중복번호','성별','경고','포인트','사용합계','충전합계']
            global root,std_treeview,std_frame
            tasd = True if dat == StudentList else False

            std_frame=tkinter.Frame(root)

            _font=Font(family="나눔 고딕", size=12,weight="bold")
            std_treeview=tkinter.ttk.Treeview(std_frame,columns=["one", "two","three","four","five","six","seven","eight","nine"], displaycolumns=["one", "two","three","four","five","six","seven","eight","nine"])
            std_treeview["height"] = 27
            style = tkinter.ttk.Style()
            style.configure("Treeview.Heading", font=("나눔 고딕", 25))

            std_verscrlbar = tkinter.ttk.Scrollbar(std_frame, 
                           orient ="vertical", 
                           command = std_treeview.yview)
            std_verscrlbar.pack(side="right", fill="y")
            
            
            std_treeview.configure(yscrollcommand = std_verscrlbar.set)

            wd = 153
            # 생년월일	학번	이름	중복번호	성별	경고	포인트	사용합계	충전합계

            std_treeview.column("#0", width=30,anchor="w")
            std_treeview.heading("#0", text="",anchor="w")

            std_treeview.column("one", width=wd, anchor="w")
            std_treeview.heading("one", text="생년월일", anchor="w")

            std_treeview.column("two", width=wd, anchor="w")
            std_treeview.heading("two", text="학번", anchor="w")

            std_treeview.column("three", width=wd, anchor="w")
            std_treeview.heading("three", text="이름", anchor="w")

            std_treeview.column("four", width=wd, anchor="w")
            std_treeview.heading("four", text="중복번호", anchor="w")

            std_treeview.column("five", width=wd, anchor="w")
            std_treeview.heading("five", text="성별", anchor="w")

            std_treeview.column("six", width=wd, anchor="w")
            std_treeview.heading("six", text="경고", anchor="w")

            std_treeview.column("seven", width=wd, anchor="w")
            std_treeview.heading("seven", text="포인트", anchor="w")

            std_treeview.column("eight", width=wd, anchor="w")
            std_treeview.heading("eight", text="사용합계", anchor="w")

            std_treeview.column("nine", width=wd, anchor="w")
            std_treeview.heading("nine", text="충전합계", anchor="w")

            treelist = fnc.std.Treebox_list(dat)
            treelist_index = [iss for iss in range(len(treelist))]
            
            for i in range(len(treelist)):
                if tasd: 
                    std_treeview.insert('', 'end', text=str(treelist_index[i]+1),values=treelist[i], iid=str(i)+"번",tags=treelist_index[i])
                    std_treeview.tag_configure(treelist_index[i] ,font=_font)
                    std_treeview.tag_bind(treelist_index[i], "<<TreeviewSelect>>", lambda event, num=i: fnc.std.ckFnc(num))
                else :   
                    std_treeview.insert('', 'end', text=dat[i],values=treelist[i], iid=str(i)+"번",tags=dat[i])
                    std_treeview.tag_configure(dat[i] ,font=_font)
                    std_treeview.tag_bind(dat[i], "<<TreeviewSelect>>", lambda event, num=dat[i]: fnc.std.ckFnc(num-1))

            std_treeview.pack(side="left")
            std_frame.place(x=100,y=250)

            root.update()
        def Treebox_list(lst):
            datas.std.LoadData()
            if lst == StudentList:
                datas.std.Load_balance()
                its = list()
                tsl = list()
                rtn = list()
                for i in range(len(StudentList[datas.std.header[0]])-1):
                    for inds in datas.std.header: # ['생년월일','학번','이름','중복번호','성별','경고','포인트','사용합계','충전합계']
                        if inds == datas.std.header[6]:
                            tsl.append(std_balances[i])
                        else: tsl.append(StudentList[inds][i+1])
                    its.append(tsl)
                    tsl = list()

                for lines in its: # 생년월일	학번	이름	중복번호	성별	경고	포인트	사용합계	충전합계
                    rtn.append(tuple(lines))

                return rtn
            else: # [index_list] ex)[1,2,3,4,...]
                datum = datas.std.search_index(lst)
                rtn = list()
                ids = 0
                for lines in datum:
                    lines[6] = std_balances[lst[ids]-1]
                    rtn.append(tuple(lines))
                    ids += 1
                return rtn
        def search():
            global std_entry,std_searchSub,root,std_indexlist,std_Treebox_info
            datas.std.LoadData()
            _stdEntry = std_entry.get()
            mode = std_searchSub.get()
            std_indexlist = list()
            if not mode in datas.std.header:
                tkinter.messagebox.showwarning("존재하지 않는 헤더값","해당 종류의 목록에서는 검색이 불가합니다. 검색 종류설정을 해주세요")
                std_searchSub.set("종류선택")
                std_Treebox_info = []
            else:
                std_indexlist = datas.std.search(mode,_stdEntry)
                fnc.std.TreeBox(std_indexlist)
                root.update()
                std_Treebox_info = [mode,_stdEntry]
        def download():
            if std_Treebox_info != [] or std_Treebox_info == [0,0]:
                if std_Treebox_info == [0,0] : _All = True
                else : _All = False
                msgbox = tkinter.messagebox.askyesno('로그 다운로드','검색된 로그 데이터를 다운로드하시겠습니까?\n\n다운로드 된 로그 데이터는 다운로드 폴더 내에 저장됩니다.')
                if msgbox:
                    datas.std.LoadData()
                    datas.std.Load_balance()
                    hdr = datas.std.header
                    datum = list()
                    if _All: 
                        lns = list()
                        for i in range(len(StudentList[datas.std.header[0]])-1):
                            for inds in hdr:
                                if inds == hdr[6]:
                                    lns.append(std_balances[i])
                                else: lns.append(StudentList[inds][i+1])
                            datum.append(lns)
                            lns = list()
                    else:datum = datas.std.search_index(std_indexlist)
                    _stdCsv = list()
                    _stdCsv.append(hdr)
                    for dt in datum:
                        _stdCsv.append(dt)
                    
                    ct = datas.log.current_time()
                    fname = str(ct[0])+str(ct[1])+str(ct[2])+str(ct[3])+str(ct[4])+str(ct[5])+"_학생목록데이터_"+str(std_Treebox_info[0])+"_"+str(std_Treebox_info[1])+".csv"
                    __path = "./다운로드/"+str(fname)

                    with open(__path, 'w', newline='') as file:
                        writer = csv.writer(file)
                        for row in _stdCsv:
                            writer.writerow(row)
                    tkinter.messagebox.showinfo("다운로드완료","{} 위치에 성공적으로 로그 데이터를 저장하였습니다.".format(__path))
        def ckFnc(num):
            global std_selected_index,std_selected_info
            std_selected_info = (datas.std.search_index([num+1]))[0]
            std_selected_index = num+1
        def point_manage():
            if std_selected_info != []:windows.student_management.additional_std.point_management()
            else:tkinter.messagebox.showerror("선택 오류","포인트에 대한 관리를 위해선 왼쪽 학생 리스트에서 학생을 선택해야 합니다. 선택 후 다시 시도해주세요.")
        def deposit_point():
            global pointEntry,pointroot,root,std_entry,std_searchSub,std_Treebox_info
            pEntryV = pointEntry.get()
            pointEntry.delete(0,len(pEntryV))
            try:
                pEntryV = int(pEntryV)
            except:
                tkinter.messagebox.showerror("입력 오류","입금하는 포인트는 자연수만 입력이 가능합니다. 다시 입력해주세요.")
            else:
                if pEntryV<=0:
                    tkinter.messagebox.showerror("입력 오류","입금하는 포인트는 자연수만 입력이 가능합니다. 다시 입력해주세요.")
                else:
                    point = int(std_balances[int(std_selected_index)-1])
                    save_point = pEntryV + point
                    datas.std.save_balance(std_selected_index,save_point)
                    datas.std.LoadData()
                    info = int((datas.std.search_index([std_selected_index]))[0][8])
                    info += int(pEntryV)
                    datas.std.modify([std_selected_index],datas.std.header[8],str(info))
                    pointroot.destroy()
                    if std_entry.get() != "":
                        fnc.std.search()
                        std_entry.delete(0,len(std_entry.get()))
                        std_searchSub.set("종류선택")
                        std_Treebox_info = []
                    fnc.std.TreeBox(StudentList)

                    root.update()
                    tkinter.messagebox.showinfo("추가 완료","{}포인트가 {}에게 추가되었습니다\n\n현재 포인트 : {}".format(pEntryV,std_selected_info[2],save_point))
        def withdraw_point():
            global pointEntry,pointroot,root,std_entry,std_searchSub,std_Treebox_info
            pEntryV = pointEntry.get()
            pointEntry.delete(0,len(pEntryV))
            try:pEntryV = int(pEntryV)
            except:tkinter.messagebox.showerror("입력 오류","출금하는 포인트는 자연수만 입력이 가능합니다. 다시 입력해주세요.")
            else:
                if pEntryV<=0:tkinter.messagebox.showerror("입력 오류","출금하는 포인트는 자연수만 입력이 가능합니다. 다시 입력해주세요.")
                else:
                    if pEntryV > int(std_balances[int(std_selected_index)-1]):tkinter.messagebox.showerror("입력 오류","출금하는 포인트가 현재 보유중인 포인트보다 많습니다. 다시 입력해주세요.")
                    else:
                        point = int(std_balances[int(std_selected_index)-1])
                        save_point = point - pEntryV
                        datas.std.save_balance(std_selected_index,save_point)
                        pointroot.destroy()
                        if std_entry.get() != "":
                            fnc.std.search()
                            std_entry.delete(0,len(std_entry.get()))
                            std_searchSub.set("종류선택")
                            std_Treebox_info = []
                        fnc.std.TreeBox(StudentList)
                        root.update()
                        tkinter.messagebox.showinfo("출금 완료","{}포인트가 {}에게서 출금되었습니다\n\n현재 포인트 : {}".format(pEntryV,std_selected_info[2],save_point))
        def warning_manage():
            if std_selected_info != []:windows.student_management.additional_std.warning()
            else:tkinter.messagebox.showerror("선택 오류","경고에 대한 관리를 위해선 왼쪽 학생 리스트에서 학생을 선택해야 합니다. 선택 후 다시 시도해주세요.")
        def warn_del():
            if int(WarningList[datas.warn.header[5]][std_selected_index]) > 0:
                msgbox = tkinter.messagebox.askyesno('정말로 경고를 차감하시겠습니까?','정말로 {} 학생의 경고를 차감하시겠습니까? 한 번 차감한 경고는 되돌리지 못합니다.'.format(str(std_selected_info[1])+str(std_selected_info[2])))
                if msgbox:
                    global warn1Text,warnCurwarn
                    datas.warn.del_warning(std_selected_index)
                    datas.warn.LoadData()
                    txt = str(std_selected_info[1])+str(std_selected_info[2])
                    txt1 = str(WarningList[datas.warn.header[5]][std_selected_index])

                    warn1Text["text"] = "1. "+str(_Warnings[std_selected_index][0])+"\n2. "+str( _Warnings[std_selected_index][1])+"\n3. "+str( _Warnings[std_selected_index][2])
                    warnCurwarn["text"] = str(StudentList[datas.warn.header[5]][int(std_selected_index)]) + "회"

                    fnc.std.TreeBox(StudentList)

                    tkinter.messagebox.showinfo("경고 차감 완료","{0} 학생의 경고가 1회 차감되었습니다. 현재 경고 횟수는 {1}회 입니다.".format(txt,txt1))
            else:
                tkinter.messagebox.showerror("제거할 경고가 없음","현재 경고횟수가 0회이므로 차감할 경고가 없습니다.")
        def warn_append():
            msgbox = tkinter.messagebox.askyesno('정말로 경고를 부여하시겠습니까?','정말로 {} 학생의 경고를 부여하시겠습니까?'.format(str(std_selected_info[1])+str(std_selected_info[2])))
            if msgbox:
                global warnroot,WAEntry,warn1Text,warnCurwarn
                warn_text = WAEntry.get()
                WAEntry.delete(0,len(warn_text))
                warn_text = warn_text.replace("/","|")
                datas.warn.add_warning(std_selected_index,warn_text)

                fnc.std.TreeBox(StudentList)

                txt = str(std_selected_info[1])+str(std_selected_info[2])
                txt1 = str(WarningList[datas.warn.header[5]][std_selected_index])

                tkinter.messagebox.showinfo("경고 부여 완료","{0} 학생의 경고가 1회 부여되었습니다. 현재 경고 횟수는 {1}회 입니다.".format(txt,txt1))

                fnc.warnadd_warn_transition()

                warn1Text["text"] = "1. "+str(_Warnings[std_selected_index][0])+"\n2. "+str( _Warnings[std_selected_index][1])+"\n3. "+str( _Warnings[std_selected_index][2])
                warnCurwarn["text"] = str(StudentList[datas.warn.header[5]][int(std_selected_index)]) + "회"
        class modify:
            def modify_manage():
                if std_selected_info != []:windows.student_management.additional_std.modify()
                else:tkinter.messagebox.showerror("선택 오류","학생 데이터에 대한 수정을 위해선 왼쪽 학생 리스트에서 학생을 선택해야 합니다. 선택 후 다시 시도해주세요.")
            def birth_edit():
                global Modify_mdfy1Bt,modifyroot,ModifyBirth
                Modify_mdfy1Bt.destroy()
                ModifyBirth.destroy()
                windows.student_management.additional_std.modify_edit.Bt1()
                modifyroot.update()
            def birth_org(sv):
                global modifyroot,_Modify_confirm1,Modify_confirm1Bt,Modify_reject1Bt,_Modify_reject1,Modify_birth_Entry,StudentList,ModifyBirth,_Modify_mdfy1,Modify_mdfy1Bt
                if sv: StudentList[datas.std.header[0]][std_selected_index] = Modify_birth_Entry.get()
                Modify_confirm1Bt.destroy()
                Modify_reject1Bt.destroy()
                Modify_birth_Entry.destroy()

                _font2 = Font(family = '맑은 고딕', size = 28,weight="bold")
                ModifyBirth = tkinter.Label(modifyroot,font=_font2,bg="#f9f4e1",anchor="w")
                ModifyBirth["text"] = StudentList[datas.std.header[0]][std_selected_index]
                ModifyBirth.place(x=125,y=117)

                _Modify_mdfy1= fnc.img("sources/imgs/buttons/mdfy.png",root=modifyroot)
                Modify_mdfy1Bt = tk.Button(modifyroot,image=_Modify_mdfy1)
                Modify_mdfy1Bt["command"] = fnc.std.modify.birth_edit
                Modify_mdfy1Bt['cursor'] = 'hand2'
                Modify_mdfy1Bt.place(x=415,y=117)
            def name_edit():
                global Modify_mdfy2Bt,modifyroot,ModifyName
                Modify_mdfy2Bt.destroy()
                ModifyName.destroy()
                windows.student_management.additional_std.modify_edit.Bt2()
                modifyroot.update()
            def name_org(sv):
                global modifyroot,_Modify_confirm2,Modify_confirm2Bt,_Modify_reject2,Modify_reject2Bt,Modify_Name_Entry,StudentList,Modify_mdfy2Bt,ModifyName,_Modify_mdfy2
                if sv : StudentList[datas.std.header[2]][std_selected_index] = Modify_Name_Entry.get()
                
                Modify_confirm2Bt.destroy()
                Modify_reject2Bt.destroy()
                Modify_Name_Entry.destroy()

                _font2 = Font(family = '맑은 고딕', size = 28,weight="bold")
                ModifyName = tkinter.Label(modifyroot,font=_font2,bg="#f9f4e1",anchor="w")
                ModifyName["text"] = StudentList[datas.std.header[2]][std_selected_index]
                ModifyName.place(x=125,y=197)

                _Modify_mdfy2= fnc.img("sources/imgs/buttons/mdfy.png",root=modifyroot)
                Modify_mdfy2Bt = tk.Button(modifyroot,image=_Modify_mdfy2)
                Modify_mdfy2Bt["command"] = fnc.std.modify.name_edit
                Modify_mdfy2Bt['cursor'] = 'hand2'
                Modify_mdfy2Bt.place(x=415,y=197)
            def stdnum_edit():
                global Modify_mdfy3Bt,modifyroot,ModifyStdNum
                Modify_mdfy3Bt.destroy()
                ModifyStdNum.destroy()
                windows.student_management.additional_std.modify_edit.Bt3()
                modifyroot.update()
            def stdnum_org(sv):
                global modifyroot,_Modify_confirm3,Modify_confirm3Bt,Modify_reject3Bt,_Modify_reject3,Modify_stdnum_Entry,StudentList,Modify_mdfy3Bt,_Modify_mdfy3
                if sv: StudentList[datas.std.header[1]][std_selected_index] = Modify_stdnum_Entry.get()

                Modify_confirm3Bt.destroy()
                Modify_reject3Bt.destroy()
                Modify_stdnum_Entry.destroy()

                _font2 = Font(family = '맑은 고딕', size = 28,weight="bold")
                ModifyStdNum = tkinter.Label(modifyroot,font=_font2,bg="#f9f4e1",anchor="w")
                ModifyStdNum["text"] = StudentList[datas.std.header[1]][std_selected_index]
                ModifyStdNum.place(x=585,y=117)

                _Modify_mdfy3= fnc.img("sources/imgs/buttons/mdfy.png",root=modifyroot)
                Modify_mdfy3Bt = tk.Button(modifyroot,image=_Modify_mdfy3)
                Modify_mdfy3Bt["command"] = fnc.std.modify.stdnum_edit
                Modify_mdfy3Bt['cursor'] = 'hand2'
                Modify_mdfy3Bt.place(x=875,y=117)
            def gender(cs):
                global modify_selected,modify_unselected,modifyroot
                if cs == 0: # 여 V 
                    if StudentList[datas.std.header[4]][std_selected_index] == "남":
                        StudentList[datas.std.header[4]][std_selected_index] = "여"
                        modify_unselected["command"] = lambda : fnc.std.modify.gender(cs=1)
                        modify_selected.place(x=800,y=190)
                        modify_unselected.place(x=650,y=190)
                if cs == 1:
                    if StudentList[datas.std.header[4]][std_selected_index] == "여":
                        StudentList[datas.std.header[4]][std_selected_index] = "남"
                        modify_unselected["command"] = lambda : fnc.std.modify.gender(cs=0)
                        modify_unselected.place(x=800,y=190)
                        modify_selected.place(x=650,y=190)  
                modifyroot.update()
            def save():
                global StudentList,modifyroot
                msgbox = tkinter.messagebox.askyesno("저장하시겠습니까?","해당 학생의 데이터를 저장하시겠습니까?")
                if msgbox:
                    datas.std.save()
                    datas.std.save_balance(std_selected_index,std_balances[std_selected_index-1])
                    fnc.std.TreeBox(StudentList)
                    modifyroot.destroy()
                    tkinter.messagebox.showinfo("저장 완료","학생 데이터가 수정되었습니다.")
            def cancel():
                global modifyroot
                modifyroot.destroy()
        def add_save():
            global addstd_birth_Entry,addstd_Name_Entry,addstd_stdnum_Entry,addstdroot
            birth = addstd_birth_Entry.get()
            name = addstd_Name_Entry.get()
            stdnum = addstd_stdnum_Entry.get()
            try: birth = int(birth)
            except : 
                addstd_birth_Entry.delete(0,len(birth))
                tkinter.messagebox.showerror("입력오류","생년월일이 올바르지 않습니다.")
            else:
                try: stdnum = int(stdnum)
                except:
                    addstd_stdnum_Entry.delete(0,len(name))
                    tkinter.messagebox.showerror("입력오류","학번이 올바르지 않습니다.")
                else:
                    if stdadd_gender == None: tkinter.messagebox.showerror("입력오류","성별이 선택되지 않았습니다. 성별을 선택해주세요.")
                    else:
                        save = True
                        msgbox = tkinter.messagebox.askyesno("등록 확인","{}{} 학생을 등록하시겠습니까?".format(stdnum,name))
                        if msgbox:
                            if str(birth) in StudentList[datas.std.header[0]] and str(name) in StudentList[datas.std.header[2]]:
                                dupnum = random.randint(2,9999)
                                sv = tkinter.messagebox.askyesno("등록 중복","{}생 {}학생은 이미 데이터베이스 상에 존재합니다. 추가로 등록하시겠습니까?\n\n만약 동명이인인 경우 이후 저장된 중복번호로 식별해야 합니다.".format(birth,name))
                                if not sv: save = False
                            else : dupnum = 1
                            if stdadd_gender == 0: gender = "남"
                            else : gender = "여"

                            if save:
                                student = [str(birth),str(stdnum),name,str(dupnum),gender,"0","0","0","0"]
                                datas.std.add(student)
                                datas.std.LoadData()
                                ind = datas.std._search(student)
                                datas.std.save_balance(ind,0)
                                datas.std.save()
                                datas.std.LoadData()
                                datas.std.Load_balance()
                                fnc.std.TreeBox(StudentList)
                                addstdroot.destroy()
                                tkinter.messagebox.showinfo("등록 완료","{}{}학생 데이터가 성공적으로 등록되었습니다.".format(stdnum,name))
        def add_cancel():
            global addstdroot,stdadd_gender
            stdadd_gender = None
            addstdroot.destroy()
        def add_gender(cs):
            global addstd_woman,addstd_man,_addstd_man,_addstd_woman,addstdroot,stdadd_gender
            tos = True
            if cs == 0:
                if stdadd_gender == None or stdadd_gender == 1:
                    stdadd_gender = 0
                elif stdadd_gender == 0:
                    stdadd_gender = None
                    _addstd_man = fnc.img("sources/imgs/buttons/unselect.png",root=addstdroot)
                    addstd_man["image"] = _addstd_man
                    addstdroot.update()
                    tos = False
            elif cs == 1:
                if stdadd_gender == None or stdadd_gender == 0:
                    stdadd_gender = 1
                elif stdadd_gender == 1:
                    stdadd_gender = None
                    _addstd_woman = fnc.img("sources/imgs/buttons/unselect.png",root=addstdroot)
                    addstd_woman["image"] = _addstd_woman
                    addstdroot.update()
                    tos = False
            
            if stdadd_gender == 0 and tos:
                _addstd_man = fnc.img("sources/imgs/buttons/select.png",root=addstdroot)
                addstd_man["image"] = _addstd_man
                _addstd_woman = fnc.img("sources/imgs/buttons/unselect.png",root=addstdroot)
                addstd_woman["image"] = _addstd_woman
                addstdroot.update()
            elif stdadd_gender == 1 and tos:
                _addstd_man = fnc.img("sources/imgs/buttons/unselect.png",root=addstdroot)
                addstd_man["image"] = _addstd_man
                _addstd_woman = fnc.img("sources/imgs/buttons/select.png",root=addstdroot)
                addstd_woman["image"] = _addstd_woman
                addstdroot.update()
        def exit():
            global addstdroot
            addstdroot.destroy()
    class stock:
        def TreeBox(dat): # ['날짜','제품군','제품명','입고/출고','개수','수익']
            global root,stock_treeview,stock_frame
            tasd = True if dat == stockLogList else False

            stock_frame=tkinter.Frame(root)

            _font=Font(family="나눔 고딕", size=12,weight="bold")
            stock_treeview=tkinter.ttk.Treeview(stock_frame,columns=["one", "two","three","four","five","six"], displaycolumns=["one", "two","three","four","five","six"])
            stock_treeview["height"] = 27
            style = tkinter.ttk.Style()
            style.configure("Treeview.Heading", font=("나눔 고딕", 20))

            stock_verscrlbar = tkinter.ttk.Scrollbar(stock_frame, 
                           orient ="vertical", 
                           command = stock_treeview.yview)
            stock_verscrlbar.pack(side="right", fill="y")
            
            
            stock_treeview.configure(yscrollcommand = stock_verscrlbar.set)

            wd = 143
            # ['날짜','제품군','제품명','입고/출고','개수','수익']

            stock_treeview.column("#0", width=30,anchor="w")
            stock_treeview.heading("#0", text="",anchor="w")

            stock_treeview.column("one", width=wd, anchor="w")
            stock_treeview.heading("one", text="날짜", anchor="w")

            stock_treeview.column("two", width=wd, anchor="w")
            stock_treeview.heading("two", text="제품군", anchor="w")

            stock_treeview.column("three", width=wd, anchor="w")
            stock_treeview.heading("three", text="제품명", anchor="w")

            stock_treeview.column("four", width=wd, anchor="w")
            stock_treeview.heading("four", text="입고/출고", anchor="w")

            stock_treeview.column("five", width=wd, anchor="w")
            stock_treeview.heading("five", text="개수", anchor="w")

            stock_treeview.column("six", width=wd, anchor="w")
            stock_treeview.heading("six", text="수익", anchor="w")

            treelist = fnc.stock.Treebox_list(dat)
            treelist_index = [iss for iss in range(len(treelist))]
            
            for i in range(len(treelist)):
                if tasd: 
                    stock_treeview.insert('', 'end', text=str(treelist_index[i]+1),values=treelist[i], iid=str(i)+"번",tags=treelist_index[i])
                    stock_treeview.tag_configure(treelist_index[i] ,font=_font)
                    stock_treeview.tag_bind(treelist_index[i], "<<TreeviewSelect>>", lambda event, num=i: fnc.stock.ckFnc(num))
                else :   
                    stock_treeview.insert('', 'end', text=dat[i],values=treelist[i], iid=str(i)+"번",tags=dat[i])
                    stock_treeview.tag_configure(dat[i] ,font=_font)
                    stock_treeview.tag_bind(dat[i], "<<TreeviewSelect>>", lambda event, num=dat[i]: fnc.stock.ckFnc(num-1))

            stock_treeview.pack(side="left")
            stock_frame.place(x=100,y=250)

            root.update()
        def Treebox_list(lst):
            if lst == stockLogList:
                its = list()
                tsl = list()
                rtn = list()
                for i in range(len(stockLogList[datas.stock.header[0]])-1):
                    for inds in datas.stock.header: # ['날짜','제품군','제품명','입고/출고','개수','수익']
                        tsl.append(stockLogList[inds][i+1])
                    its.append(tsl)
                    tsl = list()

                for lines in its: # ['날짜','제품군','제품명','입고/출고','개수','수익']
                    rtn.append(tuple(lines))

                return rtn
            else: # [index_list] ex)[1,2,3,4,...]
                datum = datas.stock.search_index(lst)
                rtn = list()
                ids = 0
                for lines in datum:
                    rtn.append(tuple(lines))
                    ids += 1
                return rtn
        def search():
            global std_entry,std_searchSub,root,std_indexlist,std_Treebox_info
            datas.std.LoadData()
            _stdEntry = std_entry.get()
            mode = std_searchSub.get()
            std_indexlist = list()
            if not mode in datas.std.header:
                tkinter.messagebox.showwarning("존재하지 않는 헤더값","해당 종류의 목록에서는 검색이 불가합니다. 검색 종류설정을 해주세요")
                std_searchSub.set("종류선택")
                std_Treebox_info = []
            else:
                std_indexlist = datas.std.search(mode,_stdEntry)
                fnc.std.TreeBox(std_indexlist)
                root.update()
                std_Treebox_info = [mode,_stdEntry]
        def ckFnc(num):
            pass
        def graph(mode,_time : list()):
            _baseYear = int(ini.read()["dat"]["기준년"])
            _baseMonth = int(ini.read()["dat"]["기준월"])
            Time_ax = list()
            Now = datetime.datetime.now()
            _Year = int(Now.year)
            _Month = int(Now.month)
            _tYtM = str(_baseYear)+"."+str(_baseMonth)
            Time_ax.append(_tYtM)
            while _baseYear != _Year or _baseMonth != _Month :
                _baseMonth += 1
                if _baseMonth > 12:
                    _baseMonth -= 12
                    _baseYear += 1
                print(_baseMonth)
                _tYtM = str(_baseYear)+"."+str(_baseMonth)
                Time_ax.append(_tYtM)
            print(Time_ax)
            datum = None
            if mode == "all":
                pass
            elif mode == "term":
                pass
            


    def pw_main_transition():
        '''
        메인-비번 -> 메인-메인 창으로의 이동함수 입니다.
        '''
        global banner,_banner,escImg,escBt,_pwbg,pwbg,rstpw,_rstpw,enter,_enter,pwE,root
        banner.destroy()
        escBt.destroy()
        pwbg.destroy()
        rstpw.destroy()
        enter.destroy()
        pwE.destroy()
        windows.main.main()
        root.bind(
                "<Return>",
                lambda event : fnc.Null()
            )
        root.update()
    def main_pw_transition():
        '''
        메인-메인 -> 메인-비번 창으로의 이동함수 입니다.
        '''
        global _banner,banner,_pdm,pdmBt,_cal,calBt,_stm,stmBt,_lgout,lgoutBt,root
        banner.destroy()
        pdmBt.destroy()
        calBt.destroy()
        stmBt.destroy()
        lgoutBt.destroy()
        windows.main.pw()
        root.update()   
    def main_pd_transition():
        '''
        메인-메인 -> 상품관리-메인 창으로의 이동함수 입니다.
        '''
        global _banner,banner,_pdm,pdmBt,_cal,calBt,_stm,stmBt,_lgout,lgoutBt,root
        banner.destroy()
        pdmBt.destroy()
        calBt.destroy()
        stmBt.destroy()
        lgoutBt.destroy()
        windows.pd_management.main()
        root.update()
    def pd_main_transition():
        '''
        상품관리-메인 -> 메인-메인 창으로의 이동함수 입니다.
        '''
        global root,_back,_pd_bg,pd_bg,pdmBanner,_pdmBanner,_add,addBt,_reload,reloadBt,_remove,removeBt,_modify,modifyBt,_left,leftBt,rightBt,_right,page,backBt,pd_btn_list,info_L
        backBt.destroy()
        pd_bg.destroy()
        pdmBanner.destroy()
        addBt.destroy()
        reloadBt.destroy()
        removeBt.destroy()
        modifyBt.destroy()
        leftBt.destroy()
        rightBt.destroy()
        page.destroy()
        info_L.destroy()
        try:
            for ins in ProductList["상품명"][1:]:
                pd_btn_list[ins].btn.destroy()
        finally:
            pd_btn_list = dict()

            windows.main.main()
            root.update()
    def main_std_transition():
        global _banner,banner,_pdm,pdmBt,_cal,calBt,_stm,stmBt,_lgout,lgoutBt,root
        banner.destroy()
        pdmBt.destroy()
        calBt.destroy()
        stmBt.destroy()
        lgoutBt.destroy()
        windows.student_management.main()
        root.update()
    def std_main_transition():
        global root,stdbanner,backBt,std_logBt,std_mgBt,stdbackBt,stdbg,stock_confirmBt
        stock_confirmBt.destroy()
        stdbackBt.destroy()
        stdbanner.destroy()
        std_logBt.destroy()
        std_mgBt.destroy()
        stdbg.destroy()
        windows.main.main()
        root.update()
    def std_log_transition():
        global root,_std_log,std_logBt,_std_mg,std_mgBt,_stdback,stdbackBt,stock_confirmBt
        stock_confirmBt.destroy()
        std_logBt.destroy()
        std_mgBt.destroy()
        stdbackBt["command"] = fnc.log_std_transition
        windows.student_management.log()
        root.update()
    def log_std_transition():
        global treeview,root,_Logsearch,Logsearch,Log_searchSub,Log_entry,_Logsearch,_LogsearchBt,_LogDownloadBt,LogDownloadBt,Log_indexlist,Treebox_info,LogsearchBt
        treeview.destroy()
        Logsearch.destroy()
        LogsearchBt.destroy()
        Log_searchSub.destroy()
        Log_entry.destroy()
        LogDownloadBt.destroy()
        Log_indexlist = list()
        Treebox_info = [0,0]
        windows.student_management.main()
        root.update()
    def std_stdm_transition():
        global root,backBt,std_logBt,std_mgBt,stdbackBt,stock_confirmBt
        stock_confirmBt.destroy()
        std_logBt.destroy()
        std_mgBt.destroy()
        stdbackBt["command"] = fnc.stdm_std_transition
        windows.student_management.studentM()
        root.update()
    def stdm_std_transition():
        global root,_stdsearch,stdsearch,stdDownloadBt,_stdDownloadBt,std_searchSub,std_entry,stdsearchBt,_stdsearchBt,_stdDepBt,stdDepBt,\
            stdreaddBt,_stdreaddBt,stdWarnBt,_stdWarnBt,stdModifyBt,_stdModifyBt,std_indexlist,std_Treebox_info
        stdsearch.destroy()
        stdDownloadBt.destroy()
        std_searchSub.destroy()
        std_entry.destroy()
        stdsearchBt.destroy()
        std_treeview.destroy()
        std_indexlist = list()
        std_Treebox_info = [0,0]
        stdDepBt.destroy()
        stdreaddBt.destroy()
        stdWarnBt.destroy()
        stdModifyBt.destroy()
        windows.student_management.main()
        root.update()
    def warn_warnadd_transition():
        global warnroot,warnbg,_warnbg,warnName,warnCurwarn,warn1Text,warnCancelBt,_warnCancelBt,warnaddBt,_warnaddBt,warndelBt,_warndelBt
        warnCurwarn.destroy()
        warn1Text.destroy()
        warnCancelBt.destroy()
        warnaddBt.destroy()
        warndelBt.destroy()
        windows.student_management.additional_std.warnadd()
        warnroot.update()
    def warnadd_warn_transition():
        global warnroot,WAbg,WAbg2,warnReason,WAEntry,_warnNoBt,warnappendBt,warnNoBt,_warnappendBt
        WAbg.destroy()
        WAbg2.destroy()
        warnReason.destroy()
        WAEntry.destroy()
        warnappendBt.destroy()
        warnNoBt.destroy()
        windows.student_management.additional_std.warn_widget()
        warnroot.update()
    def std_stdcfm_transition():
        global root,backBt,std_logBt,std_mgBt,stdbackBt,stock_confirmBt
        stock_confirmBt.destroy()
        std_logBt.destroy()
        std_mgBt.destroy()
        stdbackBt["command"] = fnc.stdcfm_std_transition
        windows.student_management.stock_income()
        root.update()
    def stdcfm_std_transition():
        windows.student_management.main()
        root.update()

class windows:
    '''
    메인 GUI에 관한 함수의 모음입니다.
    '''
    class main:
        '''
        메인 창 GUI 모음
        '''
        def init():
            '''
            기본적인 창을 생성하고 여러 함수, 데이터의 초기화를 진행합니다.
            '''
            global root
            datas.init()
            fnc.img_100x100()

            root = tk.Tk()
            root.title(title)
            root.iconbitmap(path('sources/icon.ico'))
            root.protocol('WM_DELETE_WINDOW',fnc.exit_command)
            geometry = '%dx%d+%d+%d' % (sz[0],sz[1],0,0)
            root.geometry(geometry)
            root.resizable(False,False)
            root.bind(
                "<Escape>",
                lambda event : fnc.exit_command()
            )
            root.attributes('-fullscreen', True)

            text = "{} \n 해당 프로그램의 목적에 맞지 않는 무단 배포와 조작은 금합니다. \n문의사항은 TEL 010-2017-8856 / Email justinsohn0304@naver.com 으로 주십시오.\nmade by 20210 손지형 in 2023 for 반곡고등학교".format(title,version)
            _font = Font(family = '맑은 고딕', size = 10)
            _label = tk.Label(root)
            _label['font'] = _font
            _label['text'] = text
            _label.pack(side = 'bottom')

            fnc.pd_lists_update()
            # windows.main.pw()
            windows.main.main()
            
            root.mainloop()
        def pw():
            '''
            메인-비밀번호 창에 관한 위젯 배치입니다.
            '''
            global banner,_banner,escImg,escBt,_pwbg,pwbg,rstpw,_rstpw,enter,_enter,pwE
            _banner = fnc.img("sources/imgs/banners/main.png",root=root)
            banner = tk.Label(root,image=_banner)
            banner["height"] = 440
            banner.place(x=0,y=100)

            escImg = fnc.img("sources/imgs/buttons/escape.png",root=root)
            escBt = tk.Button(root,image=escImg)
            escBt["command"] = fnc.exit_command
            escBt.place(x=1870-37,y=12)
            
            _pwbg = fnc.img("sources/imgs/bg/pwbg.png",root=root)
            pwbg = tk.Label(root,image=_pwbg)
            pwbg.place(x=180,y=600)

            _rstpw = fnc.img("sources/imgs/buttons/rstpw.png",root=root)
            rstpw = tk.Button(root,image=_rstpw)
            rstpw["command"] = windows.main.pwrst
            rstpw.place(x=700,y=875)

            _enter = fnc.img("sources/imgs/buttons/enter.png",root=root)
            enter = tk.Button(root,image=_enter)
            enter["command"] = fnc.main_pwdTest
            enter.place(x=1560,y=650)

            pwE_font = Font(family = '맑은 고딕', size = 80)
            pwE = tk.Entry(root,relief="solid",bd=5,show="*")
            pwE["width"] = 17
            pwE["insertwidth"] = 10
            pwE["font"] = pwE_font
            pwE.place(x=500,y=650)

            root.bind(
                "<Return>",
                lambda event : fnc.main_pwdTest()
            )
        def main():
            '''
            메인-메인 창에 관한 위젯 배치입니다.
            '''
            global _banner,banner,_pdm,pdmBt,_cal,calBt,_stm,stmBt,_lgout,lgoutBt
            _banner = fnc.img("sources/imgs/banners/main.png",root=root)
            banner = tk.Label(root,image=_banner)
            banner["height"] = 440
            banner.place(x=0,y=100)

            _lgout = fnc.img("sources/imgs/buttons/lgout.png",root=root)
            lgoutBt = tk.Button(root,image=_lgout)
            lgoutBt["command"] = fnc.logout
            lgoutBt.place(x=12,y=12)

            _pdm = fnc.img("sources/imgs/buttons/pdm.png",root=root)
            pdmBt = tk.Button(root,image=_pdm)
            pdmBt["command"] = fnc.main_pd_transition
            pdmBt.place(x=80,y=680)

            _cal = fnc.img("sources/imgs/buttons/cal.png",root=root)
            calBt = tk.Button(root,image=_cal)
            calBt["command"] = 0
            calBt.place(x=460+40,y=680)

            _stm = fnc.img("sources/imgs/buttons/stm.png",root=root)
            stmBt = tk.Button(root,image=_stm)
            stmBt["command"] = fnc.main_std_transition
            stmBt.place(x=460+920+40+40,y=680)

            root.update()
        def pwrst():
            '''
            메인-비밀번호 변경 팝업창 생성과 그의 위젯배치입니다.
            '''
            global proot,_pwrstbg,pwrstbg,_apply,applyBt,_deny,denyBt,existpw,newpw,repw
            def off():
                global proot
                proot.destroy()
            proot = tk.Toplevel()
            proot.protocol('WM_DELETE_WINDOW',off)

            proot.title("비밀번호 변경 / "+title)
            proot.iconbitmap(path('sources/icon.ico'))
            geometry = '%dx%d+%d+%d' % (640,760,1920/3, 150)
            proot.geometry(geometry)
            proot.resizable(False,False)
            proot.lift()
            proot.bind(
                "<Escape>",
                lambda event : off()
            )
            proot.bind(
                "<Return>",
                lambda event : fnc.change_password()
            )
            proot.grab_set()

            _pwrstbg = fnc.img("sources/imgs/bg/pwrstbg.png",root=proot)
            pwrstbg = tk.Label(proot,image=_pwrstbg)
            pwrstbg.place(x=0,y=0)

            _apply = fnc.img("sources/imgs/buttons/apply.png",root=proot)
            applyBt = tk.Button(proot,image=_apply)
            applyBt["command"] = fnc.change_password
            applyBt.place(x=40,y=600)

            _deny = fnc.img("sources/imgs/buttons/deny.png",root=proot)
            denyBt = tk.Button(proot,image=_deny)
            denyBt["command"] = off
            denyBt.place(x=360,y=600)

            _font = Font(family = '맑은 고딕', size = 35)

            existpw = tk.Entry(proot,relief="solid",bd=3,show="*")
            existpw["width"] = 18
            existpw["insertwidth"] = 6
            existpw["font"] = _font
            existpw.place(x=150,y=190)

            newpw = tk.Entry(proot,relief="solid",bd=3,show="*")
            newpw["width"] = 18
            newpw["insertwidth"] = 6
            newpw["font"] = _font
            newpw.place(x=150,y=340)

            repw = tk.Entry(proot,relief="solid",bd=3,show="*")
            repw["width"] = 18
            repw["insertwidth"] = 6
            repw["font"] = _font
            repw.place(x=150,y=490)

            proot.mainloop()
    class pd_management:
        '''
        상품관리 GUI 모음
        '''
        class _btn:
            '''
            상품 버튼 리스트의 속성을 할당하고 그에 따른 데이터를 불러와 대입합니다.
            '''
            def __init__(self,num):
                self.info = datas.pd.search_index([num])
                self.num = num
                self.img = None
                self.btn = tk.Button(root,image=self.img)
                self.btn["command"] = lambda : fnc.pd_open_info(self.info)
                self.btn['cursor'] = 'hand2'
                
                if num%5 != 0:self.y = 137 + 170*(num%5-1)
                else: self.y = 137 + 170*4
                if ((num-1)//5)%2 == 0 : self.x  = 25
                else: self.x = 25+750+30
                self.page = ((num-1)//10) + 1
        def main():
            '''
            상품관리-메인 창에 관한 위젯 배치입니다.
            '''
            global root,_back,_pd_bg,pd_bg,pdmBanner,_pdmBanner,_add,addBt,_reload,reloadBt,_remove,removeBt,_modify,modifyBt,_left,leftBt,rightBt,_right,page,backBt,info_L

            _pdmBanner = fnc.img("sources/imgs/banners/pdm.png",root=root)
            pdmBanner = tk.Label(root,image=_pdmBanner)
            pdmBanner.place(x=100,y=12)

            _pd_bg = fnc.img("sources/imgs/bg/pd_bg.png",root=root)
            pd_bg = tk.Label(root,image=_pd_bg)
            pd_bg.place(x=0,y=112)

            _back = fnc.img("sources/imgs/buttons/back.png",root=root)
            backBt = tk.Button(root,image=_back)
            backBt["command"] = fnc.pd_main_transition
            backBt['cursor'] = 'hand2'
            backBt.place(x=12,y=12)

            _reload= fnc.img("sources/imgs/buttons/reload.png",root=root)
            reloadBt = tk.Button(root,image=_reload)
            reloadBt["command"] = fnc.pd_update
            reloadBt['cursor'] = 'hand2'
            reloadBt.place(x=1825,y=12)

            _add = fnc.img("sources/imgs/buttons/add.png",root=root)
            addBt = tk.Button(root,image=_add)
            addBt["command"] = windows.pd_management.add
            addBt['cursor'] = 'hand2'
            addBt.place(x=1600,y=137)

            _remove = fnc.img("sources/imgs/buttons/remove.png",root=root)
            removeBt = tk.Button(root,image=_remove)
            removeBt["command"] = fnc.pd_remove
            removeBt['cursor'] = 'hand2'
            removeBt.place(x=1600,y=137 + 170)

            _modify = fnc.img("sources/imgs/buttons/modify.png",root=root)
            modifyBt = tk.Button(root,image=_modify)
            modifyBt["command"] = fnc.on_pd_mdfy
            modifyBt['cursor'] = 'hand2'
            modifyBt.place(x=1600,y=137 + 340)

            _left = fnc.img("sources/imgs/buttons/left.png",root=root)
            leftBt = tk.Button(root,image=_left)
            leftBt["command"] = fnc.pg_down
            leftBt['cursor'] = 'hand2'
            leftBt.place(x=1600,y=137 + 170*4 + 77)

            _right = fnc.img("sources/imgs/buttons/right.png",root=root)
            rightBt = tk.Button(root,image=_right)
            rightBt["command"] = fnc.pg_up
            rightBt['cursor'] = 'hand2'
            rightBt.place(x=1600+135+30,y=137 + 170*4 + 77)

            _font=Font(family="나눔 고딕", size=35,weight="bold")
            _font2=Font(family="나눔 고딕", size=20,weight="bold")

            info_L = tkinter.Label(root,font=_font2,bg="#ffffd9",anchor="w")
            info_L["text"] = "상품군 : -\n상품명 : -\n가격 : -\n재고 : -   \n   누적판매 : -"
            info_L.place(x=1575,y=137 + 170*3+10)

            page = tkinter.Label(root,font=_font,bg="#ffffd9")
            page["text"] = "페이지  [{}/{}]".format(pd_page,pd_page_max)
            page.place(x=1600,y=137 + 170*4+10)

            root.bind(
                "<Right>",
                lambda event : fnc.pg_up()
            )
            root.bind(
                "<Left>",
                lambda event : fnc.pg_down()
            )
            root.bind(
                "<Delete>",
                lambda event : fnc.pd_remove()
            )

            fnc.pd_update()

            root.update()
        def add():
            global addroot,_pdAddBanner,pdAddBanner,_pdAddBg,pdAddBg,pdName,_pdimg,pdimgBt,pdstock,pdprice,pdpwd,_pdadd,pdaddBt,_pdDeny,pdDenyBt\
            ,pdcomboList,pdcombobox
            def off():
                global addroot
                addroot.destroy()

            addroot = tk.Toplevel()
            addroot.protocol('WM_DELETE_WINDOW',off)

            addroot.title("상품 등록 / "+title)
            addroot.iconbitmap(path('sources/icon.ico'))
            geometry = '%dx%d+%d+%d' % (640,960,1920/3, 50)
            addroot.geometry(geometry)
            addroot.resizable(False,False)
            addroot.lift()
            addroot.bind(
                "<Escape>",
                lambda event : off()
            )
            addroot.bind(
                "<Return>",
                lambda event : fnc.pdAdd()
            )
            addroot.grab_set()

            _pdAddBanner = fnc.img("sources/imgs/banners/pd_add.png",root=addroot)
            pdAddBanner = tk.Label(addroot,image=_pdAddBanner)
            pdAddBanner.place(x=-2,y=0)

            _pdAddBg = fnc.img("sources/imgs/bg/pd_add_bg.png",root=addroot)
            pdAddBg = tk.Label(addroot,image=_pdAddBg)
            pdAddBg.place(x=-2,y=145)

            _font = Font(family = '맑은 고딕', size = 30)
            pdName = tk.Entry(addroot,relief="solid",bd=5)
            pdName["width"] = 19
            pdName["insertwidth"] = 3
            pdName["font"] = _font
            pdName.place(x=175,y=185)

            _pdimg= fnc.img("sources/imgs/buttons/imgadd.png",root=addroot)
            pdimgBt = tk.Button(addroot,image=_pdimg)
            pdimgBt["command"] = fnc.pd_imgDir
            pdimgBt['cursor'] = 'hand2'
            pdimgBt.place(x=175,y=185+125)

            pdcomboList = ini.read()["dat"]["제품군"].split(",")
            pdcombobox = tkinter.ttk.Combobox(addroot,width=12,values=pdcomboList,font=_font)
            pdcombobox.place(x=310,y=355)

            pdprice = tk.Entry(addroot,relief="solid",bd=5)
            pdprice["width"] = 19
            pdprice["insertwidth"] = 3
            pdprice["font"] = _font
            pdprice.place(x=175,y=185+285)

            pdstock = tk.Entry(addroot,relief="solid",bd=5)
            pdstock["width"] = 19
            pdstock["insertwidth"] = 3
            pdstock["font"] = _font
            pdstock.place(x=175,y=185+285+155)

            pdpwd = tk.Entry(addroot,relief="solid",bd=5,show="*")
            pdpwd["width"] = 19
            pdpwd["insertwidth"] = 3
            pdpwd["font"] = _font
            pdpwd.place(x=175,y=185+285+155 + 145)

            _pdDeny = fnc.img("sources/imgs/buttons/pddeny.png",root=addroot)
            pdDenyBt = tk.Button(addroot,image=_pdDeny)
            pdDenyBt["command"] = off
            pdDenyBt['cursor'] = 'hand2'
            pdDenyBt.place(x=50,y=850)

            _pdadd = fnc.img("sources/imgs/buttons/pdadd.png",root=addroot)
            pdaddBt = tk.Button(addroot,image=_pdadd)
            pdaddBt["command"] = fnc.pdAdd
            pdaddBt['cursor'] = 'hand2'
            pdaddBt.place(x=350,y=850)

            addroot.mainloop()
        def modify():
            global mdfyroot,_pdModifyBanner,pdModifyBanner,_pd_mdfybg,pd_mdfybg,_pdcancel,pdcancelBt,pdsaveBt,_pdsave,\
                _pdmdfy1,pdmdfy1Bt,_pdmdfy2,pdmdfy2Bt,_pdmdfy3,pdmdfy3Bt,_pdrdimg,pdrdimgBt,item_name,pd_modify,mdfy_index,pdcomboboxmdfy
            mdfy_index = datas.pd._search(pd_selected)
            def off():
                global mdfyroot,pd_modify
                pd_modify = [False,False,False]
                mdfyroot.destroy()

            mdfyroot = tk.Toplevel()
            mdfyroot.protocol('WM_DELETE_WINDOW',off)

            mdfyroot.title("상품 정보 수정 / "+title)
            mdfyroot.iconbitmap(path('sources/icon.ico'))
            geometry = '%dx%d+%d+%d' % (640,960,1920/3, 50)
            mdfyroot.geometry(geometry)
            mdfyroot.resizable(False,False)
            mdfyroot.lift()
            mdfyroot.bind(
                "<Escape>",
                lambda event : off()
            )
            mdfyroot.bind(
                "<Return>",
                lambda event : fnc.Null()
            )
            mdfyroot.grab_set()

            _pdModifyBanner = fnc.img("sources/imgs/banners/pd_modify.png",root=mdfyroot)
            pdModifyBanner = tk.Label(mdfyroot,image=_pdModifyBanner)
            pdModifyBanner.place(x=-2,y=0)

            _pd_mdfybg = fnc.img("sources/imgs/bg/pd_modify.png",root=mdfyroot)
            pd_mdfybg = tk.Label(mdfyroot,image=_pd_mdfybg)
            pd_mdfybg.place(x=-2,y=150)

            windows.pd_management.mdfy_ud()

            _font = Font(family = '맑은 고딕', size = 30)

            pdcombomdfyList = ini.read()["dat"]["제품군"].split(",")
            pdcomboboxmdfy = tkinter.ttk.Combobox(mdfyroot,width=12,values=pdcombomdfyList,font=_font)
            pdcmf = pd_selected[6]
            pdcomboboxmdfy.set(pdcmf)
            pdcomboboxmdfy.place(x=310,y=770)

            _pdcancel= fnc.img("sources/imgs/buttons/pddeny.png",root=mdfyroot)
            pdcancelBt = tk.Button(mdfyroot,image=_pdcancel)
            pdcancelBt["command"] = fnc.pd_mdfy.cas
            pdcancelBt['cursor'] = 'hand2'
            pdcancelBt.place(x=25,y=850)

            _pdsave= fnc.img("sources/imgs/buttons/save.png",root=mdfyroot)
            pdsaveBt = tk.Button(mdfyroot,image=_pdsave)
            pdsaveBt["command"] = fnc.pd_mdfy.save
            pdsaveBt['cursor'] = 'hand2'
            pdsaveBt.place(x=350,y=850)

            mdfyroot.mainloop()
        class mdfy_udc:
            def _1f():
                global _pdmdfy1,pdmdfy1Bt,item_name
                _font=Font(family="나눔 고딕", size=35,weight="bold")
                _pdmdfy1= fnc.img("sources/imgs/buttons/mdfy.png",root=mdfyroot)
                pdmdfy1Bt = tk.Button(mdfyroot,image=_pdmdfy1)
                pdmdfy1Bt["command"] = lambda : fnc.pd_mdfy.edit(0)
                pdmdfy1Bt['cursor'] = 'hand2'
                pdmdfy1Bt.place(x=550,y=220)

                item_name = tkinter.Label(mdfyroot,font=_font,bg="#efe4b0",anchor="w")
                item_name["text"] = pd_selected[1]
                item_name.place(x=175,y=220)
            def _1t():
                global _pdconfirm1,pdconfirm1Bt,_pdcancel1,pdcancel1Bt,_NameEntry
                _font=Font(family="나눔 고딕", size=35,weight="bold")
                _pdconfirm1= fnc.img("sources/imgs/buttons/confirm.png",root=mdfyroot)
                pdconfirm1Bt = tk.Button(mdfyroot,image=_pdconfirm1)
                pdconfirm1Bt["command"] = lambda : fnc.pd_mdfy.confirm(0)
                pdconfirm1Bt['cursor'] = 'hand2'
                pdconfirm1Bt.place(x=550,y=300)

                _pdcancel1= fnc.img("sources/imgs/buttons/cancel.png",root=mdfyroot)
                pdcancel1Bt = tk.Button(mdfyroot,image=_pdcancel1)
                pdcancel1Bt["command"] = lambda : fnc.pd_mdfy.cancel(0)
                pdcancel1Bt['cursor'] = 'hand2'
                pdcancel1Bt.place(x=550-70,y=300)

                _NameEntry = tk.Entry(mdfyroot,relief="solid",bd=3)
                _NameEntry["width"] = 16
                _NameEntry["insertwidth"] = 6
                _NameEntry["font"] = _font
                _NameEntry.place(x=175,y=217)

                _NameEntry.insert(0,pd_selected[1])
            def _2f():
                global pdmdfy2Bt,_pdmdfy2,item_price
                _font=Font(family="나눔 고딕", size=35,weight="bold")
                _pdmdfy2= fnc.img("sources/imgs/buttons/mdfy.png",root=mdfyroot)
                pdmdfy2Bt = tk.Button(mdfyroot,image=_pdmdfy2)
                pdmdfy2Bt["command"] = lambda : fnc.pd_mdfy.edit(1)
                pdmdfy2Bt['cursor'] = 'hand2'
                pdmdfy2Bt.place(x=550,y=385)

                item_price = tkinter.Label(mdfyroot,font=_font,bg="#efe4b0",anchor="w")
                item_price["text"] = pd_selected[3]
                item_price.place(x=175,y=450-67)
            def _2t():
                global pdconfirm2Bt,_pdconfirm2,pdcancel2Bt,_pdcancel2,_PriceEntry
                _font=Font(family="나눔 고딕", size=35,weight="bold")
                _pdconfirm2= fnc.img("sources/imgs/buttons/confirm.png",root=mdfyroot)
                pdconfirm2Bt = tk.Button(mdfyroot,image=_pdconfirm2)
                pdconfirm2Bt["command"] = lambda : fnc.pd_mdfy.confirm(1)
                pdconfirm2Bt['cursor'] = 'hand2'
                pdconfirm2Bt.place(x=550,y=465)

                _pdcancel2= fnc.img("sources/imgs/buttons/cancel.png",root=mdfyroot)
                pdcancel2Bt = tk.Button(mdfyroot,image=_pdcancel2)
                pdcancel2Bt["command"] = lambda : fnc.pd_mdfy.cancel(1)
                pdcancel2Bt['cursor'] = 'hand2'
                pdcancel2Bt.place(x=550-70,y=465)

                _PriceEntry = tk.Entry(mdfyroot,relief="solid")
                _PriceEntry["width"] = 16
                _PriceEntry["insertwidth"] = 6
                _PriceEntry["font"] = _font
                _PriceEntry.place(x=175,y=450-67)

                _PriceEntry.insert(0,pd_selected[3])
            def _3f():
                global pdmdfy3Bt,_pdmdfy3,item_stock
                _font=Font(family="나눔 고딕", size=35,weight="bold")
                _pdmdfy3= fnc.img("sources/imgs/buttons/mdfy.png",root=mdfyroot)
                pdmdfy3Bt = tk.Button(mdfyroot,image=_pdmdfy3)
                pdmdfy3Bt["command"] = lambda : fnc.pd_mdfy.edit(2)
                pdmdfy3Bt['cursor'] = 'hand2'
                pdmdfy3Bt.place(x=550,y=575)

                item_stock = tkinter.Label(mdfyroot,font=_font,bg="#efe4b0",anchor="w")
                item_stock["text"] = pd_selected[4]
                item_stock.place(x=175,y=573)
            def _3t():
                global pdcancel3Bt,_pdcancel3,pdminusBt,_pdminus,_pdplus,pdplusBt,pdsetBt,_pdset,_StockEntry
                _font=Font(family="나눔 고딕", size=35,weight="bold")
                _pdcancel3= fnc.img("sources/imgs/buttons/cancel.png",root=mdfyroot)
                pdcancel3Bt = tk.Button(mdfyroot,image=_pdcancel3)
                pdcancel3Bt["command"] = lambda : fnc.pd_mdfy.cancel(2)
                pdcancel3Bt['cursor'] = 'hand2'
                pdcancel3Bt.place(x=550-240,y=655)

                _pdminus= fnc.img("sources/imgs/buttons/minus.png",root=mdfyroot)
                pdminusBt = tk.Button(mdfyroot,image=_pdminus)
                pdminusBt["command"] = lambda : fnc.pd_mdfy.confirm(2)
                pdminusBt['cursor'] = 'hand2'
                pdminusBt.place(x=550-140,y=655)

                _pdset= fnc.img("sources/imgs/buttons/set.png",root=mdfyroot)
                pdsetBt = tk.Button(mdfyroot,image=_pdset)
                pdsetBt["command"] = lambda : fnc.pd_mdfy.confirm(3)
                pdsetBt['cursor'] = 'hand2'
                pdsetBt.place(x=550-70,y=655)

                _pdplus= fnc.img("sources/imgs/buttons/plus.png",root=mdfyroot)
                pdplusBt = tk.Button(mdfyroot,image=_pdplus)
                pdplusBt["command"] = lambda : fnc.pd_mdfy.confirm(4)
                pdplusBt['cursor'] = 'hand2'
                pdplusBt.place(x=550,y=655)

                _StockEntry = tk.Entry(mdfyroot,relief="solid")
                _StockEntry["width"] = 16
                _StockEntry["insertwidth"] = 6
                _StockEntry["font"] = _font
                _StockEntry.place(x=175,y=570)

                _StockEntry.insert(0,"0")
        def mdfy_ud():
            global mdfyroot,_pdModifyBanner,pdModifyBanner,_pd_mdfybg,pd_mdfybg,_pdcancel,pdcancelBt,pdsaveBt,_pdsave,\
                _pdmdfy1,pdmdfy1Bt,_pdmdfy2,pdmdfy2Bt,_pdmdfy3,pdmdfy3Bt,_pdrdimg,pdrdimgBt,item_name,item_price,item_stock,\
                _pdconfirm1,_pdconfirm2,pdconfirm1Bt,pdconfirm2Bt,_NameEntry,_PriceEntry,_pdminus,pdminusBt,_pdplus,pdplusBt,\
                _pdset,pdsetBt,_StockEntry,_pdcancel1,_pdcancel2,_pdcancel3,pdcancel1Bt,pdcancel2Bt,pdcancel3Bt,pd_modify

            if not pd_modify[0] : windows.pd_management.mdfy_udc._1f()
            else:                 windows.pd_management.mdfy_udc._1t()
            
            if not pd_modify[1] : windows.pd_management.mdfy_udc._2f()
            else :                windows.pd_management.mdfy_udc._2t()
            
            if not pd_modify[2] : windows.pd_management.mdfy_udc._3f()
            else:                 windows.pd_management.mdfy_udc._3t()

            if pd_selected[2] != "-":
                _pdrdimg= fnc.img("sources/imgs/100x100/"+pd_selected[2],root=mdfyroot)
            else:
                _pdrdimg= fnc.img("sources/imgs/buttons/No_img.png",root=mdfyroot)

            pdrdimgBt = tk.Button(mdfyroot,image=_pdrdimg)
            pdrdimgBt["command"] = fnc.pd_mdfy.img
            pdrdimgBt['cursor'] = 'hand2'
            pdrdimgBt.place(x=175,y=725)

            mdfyroot.update()
    class student_management:
        def main():
            global root,_stdbanner,stdbanner,_std_log,std_logBt,_std_mg,std_mgBt,_stdback,stdbackBt,stdbg,_stdbg,_stock_confirm,stock_confirmBt

            _stdbg = fnc.img("sources/imgs/bg/log.png",root=root)
            stdbg = tk.Label(root,image=_stdbg)
            stdbg.place(x=-2,y=200)

            _stdbanner = fnc.img("sources/imgs/banners/std_management.png",root=root)
            stdbanner = tk.Label(root,image=_stdbanner)
            stdbanner.place(x=-2,y=-2)

            _stdback = fnc.img("sources/imgs/buttons/back.png",root=root)
            stdbackBt = tk.Button(root,image=_stdback)
            stdbackBt["command"] = fnc.std_main_transition
            stdbackBt['cursor'] = 'hand2'
            stdbackBt.place(x=12,y=75)

            _std_log = fnc.img("sources/imgs/buttons/std_log.png",root=root)
            std_logBt = tk.Button(root,image=_std_log)
            std_logBt["command"] = fnc.std_log_transition
            std_logBt["cursor"] = 'hand2'
            std_logBt.place(x=50,y=350)

            _std_mg = fnc.img("sources/imgs/buttons/std_mg.png",root=root)
            std_mgBt = tk.Button(root,image=_std_mg)
            std_mgBt["command"] = fnc.std_stdm_transition
            std_mgBt["cursor"] = 'hand2'
            std_mgBt.place(x=1020,y=350)

            _stock_confirm = fnc.img("sources/imgs/buttons/stock_confirm.png",root=root)
            stock_confirmBt = tk.Button(root,image=_stock_confirm)
            stock_confirmBt["command"] = fnc.std_stdcfm_transition
            stock_confirmBt["cursor"] = 'hand2'
            stock_confirmBt.place(x=550,y=650)

            root.update()
        def log():
            global _Logsearch,Logsearch,Log_searchSub,Log_entry,_Logsearch,Logsearch,_LogsearchBt,_LogDownloadBt,LogDownloadBt,LogsearchBt
            root.bind(
                "<Return>",
                lambda event : fnc.log.search()
            )
            
            _font = Font(family = '맑은 고딕', size = 35)
            _font2 = Font(family = '맑은 고딕', size = 20)

            search_list = datas.log.header

            _Logsearch = fnc.img("sources/imgs/bg/search.png",root=root)
            Logsearch = tk.Label(root,image=_Logsearch)
            Logsearch.place(x=-2,y=850)

            fnc.log.TreeBox(UsingLog)

            _LogDownloadBt = fnc.img("sources/imgs/buttons/download.png",root=root)
            LogDownloadBt = tk.Button(root,image=_LogDownloadBt)
            LogDownloadBt["command"] = fnc.log.download
            LogDownloadBt['cursor'] = 'hand2'
            LogDownloadBt.place(x=1835,y=745)

            Log_searchSub = tkinter.ttk.Combobox(root,height=7,font=_font)
            Log_searchSub["values"] = search_list
            Log_searchSub["width"] = 8
            Log_searchSub["height"] = 8
            root.option_add("*TCombobox*Listbox*Font", _font2)
            Log_searchSub.set("종류선택")
            Log_searchSub.place(x=250,y=892)

            Log_entry = tk.Entry(root,font=_font,bd=4)
            Log_entry["width"] = 40
            Log_entry.place(x=550,y=892)

            _LogsearchBt = fnc.img("sources/imgs/buttons/stdsearch.png",root=root)
            LogsearchBt = tk.Button(root,image=_LogsearchBt)
            LogsearchBt["command"] = fnc.log.search
            LogsearchBt['cursor'] = 'hand2'
            LogsearchBt.place(x=1675,y=875)

            root.update()
        def studentM():
            global root,_stdsearch,stdsearch,stdDownloadBt,_stdDownloadBt,std_searchSub,std_entry,stdsearchBt,_stdsearchBt,_stdDepBt,stdDepBt,\
            stdreaddBt,_stdreaddBt,stdWarnBt,_stdWarnBt,stdModifyBt,_stdModifyBt
            root.bind(
                "<Return>",
                lambda event : fnc.std.search()
            )
            
            _font = Font(family = '맑은 고딕', size = 35)
            _font2 = Font(family = '맑은 고딕', size = 20)

            search_list = datas.std.header

            _stdsearch = fnc.img("sources/imgs/bg/search.png",root=root)
            stdsearch = tk.Label(root,image=_stdsearch)
            stdsearch.place(x=-2,y=850)

            fnc.std.TreeBox(StudentList)

            _stdDownloadBt = fnc.img("sources/imgs/buttons/download.png",root=root)
            stdDownloadBt = tk.Button(root,image=_stdDownloadBt)
            stdDownloadBt["command"] = fnc.std.download
            stdDownloadBt['cursor'] = 'hand2'
            stdDownloadBt.place(x=1690,y=745)

            std_searchSub = tkinter.ttk.Combobox(root,height=7,font=_font)
            std_searchSub["values"] = search_list
            std_searchSub["width"] = 8
            std_searchSub["height"] = 8
            root.option_add("*TCombobox*Listbox*Font", _font2)
            std_searchSub.set("종류선택")
            std_searchSub.place(x=250,y=892)

            std_entry = tk.Entry(root,font=_font,bd=4)
            std_entry["width"] = 40
            std_entry.place(x=550,y=892)

            _stdsearchBt = fnc.img("sources/imgs/buttons/stdsearch.png",root=root)
            stdsearchBt = tk.Button(root,image=_stdsearchBt)
            stdsearchBt["command"] = fnc.std.search
            stdsearchBt['cursor'] = 'hand2'
            stdsearchBt.place(x=1675,y=875)

            _stdDepBt = fnc.img("sources/imgs/buttons/point.png",root=root)
            stdDepBt = tk.Button(root,image=_stdDepBt)
            stdDepBt["command"] = fnc.std.point_manage
            stdDepBt['cursor'] = 'hand2'
            stdDepBt.place(x=1555,y=250)


            _stdWarnBt = fnc.img("sources/imgs/buttons/warning.png",root=root)
            stdWarnBt = tk.Button(root,image=_stdWarnBt)
            stdWarnBt["command"] = fnc.std.warning_manage
            stdWarnBt['cursor'] = 'hand2'
            stdWarnBt.place(x=1555,y=375)

            _stdModifyBt = fnc.img("sources/imgs/buttons/std_modify.png",root=root)
            stdModifyBt = tk.Button(root,image=_stdModifyBt)
            stdModifyBt["command"] = fnc.std.modify.modify_manage
            stdModifyBt['cursor'] = 'hand2'
            stdModifyBt.place(x=1555,y=500)

            _stdreaddBt = fnc.img("sources/imgs/buttons/std_add.png",root=root)
            stdreaddBt = tk.Button(root,image=_stdreaddBt)
            stdreaddBt["command"] = windows.student_management.additional_std.add_student
            stdreaddBt['cursor'] = 'hand2'
            stdreaddBt.place(x=1555,y=625)

            root.update()
        class additional_std:
            def point_management():
                global pointroot,_pointbg,pointbg,pointName,pointCurP,_pointCancelBt,pointCancelBt,pointDepositBt,_pointDepositBt,pointwithdrawBt,_pointwithdrawBt,pointEntry
                def off():
                    global pointroot
                    pointroot.destroy()
                pointroot = tk.Toplevel()
                pointroot.protocol('WM_DELETE_WINDOW',off)

                pointroot.title("포인트 관리 / "+title)
                pointroot.iconbitmap(path('sources/icon.ico'))
                geometry = '%dx%d+%d+%d' % (960,360,(1920-960)/2, (1080-360)/2)
                pointroot.geometry(geometry)
                pointroot.resizable(False,False)
                pointroot.lift()
                pointroot.bind(
                    "<Escape>",
                    lambda event : off()
                )
                pointroot.grab_set()

                _font = Font(family = '맑은 고딕', size = 28)
                _font2 = Font(family = '맑은 고딕', size = 35,weight="bold")

                _pointbg = fnc.img("sources/imgs/bg/point.png",root=pointroot)
                pointbg = tk.Label(pointroot,image=_pointbg)
                pointbg.place(x=-2,y=0)

                pointName = tkinter.Label(pointroot,font=_font2,bg="#efe4b0",anchor="w")
                pointName["text"] = str( std_selected_info[1] ) + str( std_selected_info[2] )
                pointName.place(x=175,y=26)

                pointCurP = tkinter.Label(pointroot,font=_font2,bg="#ffffff",anchor="w")
                pointCurP["text"] = str(std_balances[int(std_selected_index)-1]) + "포인트"
                pointCurP.place(x=475,y=102)

                pointEntry = tk.Entry(pointroot,font=_font,bd=4)
                pointEntry["width"] = 16
                pointEntry.place(x=475,y=185)

                _pointCancelBt = fnc.img("sources/imgs/buttons/pddeny.png",root=pointroot)
                pointCancelBt = tk.Button(pointroot,image=_pointCancelBt)
                pointCancelBt["command"] = off
                pointCancelBt['cursor'] = 'hand2'
                pointCancelBt.place(x=25,y=265)

                _pointDepositBt = fnc.img("sources/imgs/buttons/point_deposit.png",root=pointroot)
                pointDepositBt = tk.Button(pointroot,image=_pointDepositBt)
                pointDepositBt["command"] = fnc.std.deposit_point
                pointDepositBt['cursor'] = 'hand2'
                pointDepositBt.place(x=700,y=265)

                _pointwithdrawBt = fnc.img("sources/imgs/buttons/point_withdraw.png",root=pointroot)
                pointwithdrawBt = tk.Button(pointroot,image=_pointwithdrawBt)
                pointwithdrawBt["command"] = fnc.std.withdraw_point
                pointwithdrawBt['cursor'] = 'hand2'
                pointwithdrawBt.place(x=450,y=265)
            def warning():
                global warnroot

                def off():
                    global warnroot
                    warnroot.destroy()
                warnroot = tk.Toplevel()
                warnroot.protocol('WM_DELETE_WINDOW',off)

                warnroot.title("경고 부여 / "+title)
                warnroot.iconbitmap(path('sources/icon.ico'))
                geometry = '%dx%d+%d+%d' % (960,360,(1920-960)/2, (1080-360)/2)
                warnroot.geometry(geometry)
                warnroot.resizable(False,False)
                warnroot.lift()
                warnroot.bind(
                    "<Escape>",
                    lambda event : off()
                )
                warnroot.bind(
                    "<Return>",
                    lambda event : fnc.Null()
                )
                warnroot.grab_set()

                windows.student_management.additional_std.warn_widget()
            def warn_widget():
                def off():
                    global warnroot
                    warnroot.destroy()
                global warnroot,warnbg,_warnbg,warnName,warnCurwarn,warn1Text,warnCancelBt,_warnCancelBt,warnaddBt,_warnaddBt,warndelBt,_warndelBt
                _font = Font(family = '맑은 고딕', size = 28,weight="bold")
                _font2 = Font(family = '맑은 고딕', size = 35,weight="bold")
                _font3 = Font(family = '맑은 고딕', size = 16)

                _warnbg = fnc.img("sources/imgs/bg/warnrootbg.png",root=warnroot)
                warnbg = tk.Label(warnroot,image=_warnbg)
                warnbg.place(x=-2,y=0)

                warnName = tkinter.Label(warnroot,font=_font2,bg="#efe4b0",anchor="w")
                warnName["text"] = str( std_selected_info[1] ) + str( std_selected_info[2] )
                warnName.place(x=175,y=26)

                warnCurwarn = tkinter.Label(warnroot,font=_font,bg="#ffffff",anchor="w")
                warnCurwarn["text"] = str(StudentList[datas.warn.header[5]][int(std_selected_index)]) + "회"
                warnCurwarn.place(x=325,y=110)

                warn1Text = tkinter.Label(warnroot,font=_font3,bg='#ffeef3')
                warn1Text["text"] = "1. "+str(_Warnings[std_selected_index][0])+"\n2. "+str( _Warnings[std_selected_index][1])+"\n3. "+str( _Warnings[std_selected_index][2])
                warn1Text["width"] = 28
                warn1Text["height"] = 4
                warn1Text["anchor"] = "w"
                warn1Text.place(x=600,y=115)

                _warnCancelBt = fnc.img("sources/imgs/buttons/pddeny.png",root=warnroot)
                warnCancelBt = tk.Button(warnroot,image=_warnCancelBt)
                warnCancelBt["command"] = off
                warnCancelBt['cursor'] = 'hand2'
                warnCancelBt.place(x=25,y=265)

                _warnaddBt = fnc.img("sources/imgs/buttons/warnadd.png",root=warnroot)
                warnaddBt = tk.Button(warnroot,image=_warnaddBt)
                warnaddBt["command"] = fnc.warn_warnadd_transition
                warnaddBt['cursor'] = 'hand2'
                warnaddBt.place(x=450,y=265)

                _warndelBt = fnc.img("sources/imgs/buttons/warndel.png",root=warnroot)
                warndelBt = tk.Button(warnroot,image=_warndelBt)
                warndelBt["command"] = fnc.std.warn_del
                warndelBt['cursor'] = 'hand2'
                warndelBt.place(x=700,y=265)


                warnroot.mainloop()
            def warnadd():
                global warnroot,WAbg,WAbg2,warnReason,WAEntry,_warnNoBt,warnappendBt,warnNoBt,_warnappendBt
                _font2 = Font(family = '맑은 고딕', size = 30,weight="bold")

                WAbg = tkinter.Label(warnroot,bg="#ffffff",anchor="w")
                WAbg["height"] = 15
                WAbg["width"] = 120
                WAbg.place(x=10,y=110)
                
                WAbg2 = tkinter.Label(warnroot,bg="#efe4b0",anchor="w")
                WAbg2["height"] = 5
                WAbg2["width"] = 125
                WAbg2.place(x=40,y=175)

                warnReason = tkinter.Label(warnroot,font=_font2,bg="#ffffff")
                warnReason["text"] = "경고 사유 입력"
                warnReason["anchor"] = "w"
                warnReason.place(x=60,y=110)

                WAEntry_font = Font(family = '맑은 고딕', size = 28)
                WAEntry = tk.Entry(warnroot,relief="solid",bd=5)
                WAEntry["width"] = 41
                WAEntry["insertwidth"] = 7
                WAEntry["font"] = WAEntry_font
                WAEntry.place(x=60,y=185)

                _warnNoBt = fnc.img("sources/imgs/buttons/warncan.png",root=warnroot)
                warnNoBt = tk.Button(warnroot,image=_warnNoBt)
                warnNoBt["command"] = fnc.warnadd_warn_transition
                warnNoBt['cursor'] = 'hand2'
                warnNoBt.place(x=25,y=265)

                _warnappendBt = fnc.img("sources/imgs/buttons/warnappend.png",root=warnroot)
                warnappendBt = tk.Button(warnroot,image=_warnappendBt)
                warnappendBt["command"] = fnc.std.warn_append
                warnappendBt['cursor'] = 'hand2'
                warnappendBt.place(x=700,y=265)
                

                warnroot.update()
            def modify():
                global modifyroot

                def off():
                    global modifyroot
                    modifyroot.destroy()
                modifyroot = tk.Toplevel()
                modifyroot.protocol('WM_DELETE_WINDOW',off)

                modifyroot.title("학생 정보 수정 / "+title)
                modifyroot.iconbitmap(path('sources/icon.ico'))
                geometry = '%dx%d+%d+%d' % (960,360,(1920-960)/2, (1080-360)/2)
                modifyroot.geometry(geometry)
                modifyroot.resizable(False,False)
                modifyroot.lift()
                modifyroot.bind(
                    "<Escape>",
                    lambda event : off()
                )
                modifyroot.bind(
                    "<Return>",
                    lambda event : fnc.Null()
                )
                modifyroot.grab_set()

                windows.student_management.additional_std.modify_widget()
            def modify_widget():
                global modifyroot,_modifybg,modifybg,ModifyName,ModifyBirth,ModifyStdNum,_Modify_mdfy1,Modify_mdfy1Bt,_Modify_mdfy2,Modify_mdfy2Bt,_Modify_mdfy3,Modify_mdfy3Bt,\
                    modify_selected,modify_unselected,_modify_selected,_modify_unselected,_Modify_save,Modify_saveBt,_Modify_cancel,Modify_cancelBt
                
                _font = Font(family = '맑은 고딕', size = 35,weight="bold")
                _font2 = Font(family = '맑은 고딕', size = 28,weight="bold")

                _modifybg = fnc.img("sources/imgs/bg/modifyroot_bg.png",root=modifyroot)
                modifybg = tk.Label(modifyroot,image=_modifybg)
                modifybg.place(x=-2,y=0)

                StdModifyName = tkinter.Label(modifyroot,font=_font,bg="#efe4b0",anchor="w")
                StdModifyName["text"] = str( std_selected_info[1] ) + str( std_selected_info[2] )
                StdModifyName.place(x=175,y=26)

                ModifyBirth = tkinter.Label(modifyroot,font=_font2,bg="#f9f4e1",anchor="w")
                ModifyBirth["text"] = StudentList[datas.std.header[0]][std_selected_index]
                ModifyBirth.place(x=125,y=117)

                _Modify_mdfy1= fnc.img("sources/imgs/buttons/mdfy.png",root=modifyroot)
                Modify_mdfy1Bt = tk.Button(modifyroot,image=_Modify_mdfy1)
                Modify_mdfy1Bt["command"] = fnc.std.modify.birth_edit
                Modify_mdfy1Bt['cursor'] = 'hand2'
                Modify_mdfy1Bt.place(x=415,y=117)

                ModifyName = tkinter.Label(modifyroot,font=_font2,bg="#f9f4e1",anchor="w")
                ModifyName["text"] = StudentList[datas.std.header[2]][std_selected_index]
                ModifyName.place(x=125,y=197)

                _Modify_mdfy2= fnc.img("sources/imgs/buttons/mdfy.png",root=modifyroot)
                Modify_mdfy2Bt = tk.Button(modifyroot,image=_Modify_mdfy2)
                Modify_mdfy2Bt["command"] = fnc.std.modify.name_edit
                Modify_mdfy2Bt['cursor'] = 'hand2'
                Modify_mdfy2Bt.place(x=415,y=197)

                ModifyStdNum = tkinter.Label(modifyroot,font=_font2,bg="#f9f4e1",anchor="w")
                ModifyStdNum["text"] = StudentList[datas.std.header[1]][std_selected_index]
                ModifyStdNum.place(x=585,y=117)

                _Modify_mdfy3= fnc.img("sources/imgs/buttons/mdfy.png",root=modifyroot)
                Modify_mdfy3Bt = tk.Button(modifyroot,image=_Modify_mdfy3)
                Modify_mdfy3Bt["command"] = fnc.std.modify.stdnum_edit
                Modify_mdfy3Bt['cursor'] = 'hand2'
                Modify_mdfy3Bt.place(x=875,y=117)

                _modify_unselected = fnc.img("sources/imgs/buttons/unselect.png",root=modifyroot)
                modify_unselected = tk.Button(modifyroot,image=_modify_unselected)
                modify_unselected['cursor'] = 'hand2'
                _modify_selected = fnc.img("sources/imgs/buttons/select.png",root=modifyroot)
                modify_selected = tk.Button(modifyroot,image=_modify_selected)
                modify_selected["command"] = fnc.Null
                modify_selected['cursor'] = 'hand2'
                if StudentList[datas.std.header[4]][std_selected_index] == "남":
                    modify_unselected["command"] = lambda : fnc.std.modify.gender(cs=0)
                    modify_unselected.place(x=800,y=190)
                    modify_selected.place(x=650,y=190)
                else:
                    modify_unselected["command"] = lambda : fnc.std.modify.gender(cs=1)
                    modify_selected.place(x=800,y=190)
                    modify_unselected.place(x=650,y=190)

                _Modify_save= fnc.img("sources/imgs/buttons/save.png",root=modifyroot)
                Modify_saveBt = tk.Button(modifyroot,image=_Modify_save)
                Modify_saveBt["command"] = fnc.std.modify.save
                Modify_saveBt['cursor'] = 'hand2'
                Modify_saveBt.place(x=675,y=275)

                _Modify_cancel= fnc.img("sources/imgs/buttons/pddeny.png",root=modifyroot)
                Modify_cancelBt = tk.Button(modifyroot,image=_Modify_cancel)
                Modify_cancelBt["command"] = fnc.std.modify.cancel
                Modify_cancelBt['cursor'] = 'hand2'
                Modify_cancelBt.place(x=30,y=275)
            class modify_edit:
                def Bt1():
                    global modifyroot,_Modify_confirm1,Modify_confirm1Bt,Modify_reject1Bt,_Modify_reject1,Modify_birth_Entry
                    _Modify_confirm1= fnc.img("sources/imgs/buttons/confirm.png",root=modifyroot)
                    Modify_confirm1Bt = tk.Button(modifyroot,image=_Modify_confirm1)
                    Modify_confirm1Bt["command"] = lambda : fnc.std.modify.birth_org(True)
                    Modify_confirm1Bt['cursor'] = 'hand2'
                    Modify_confirm1Bt.place(x=415,y=117)

                    _Modify_reject1= fnc.img("sources/imgs/buttons/cancel.png",root=modifyroot)
                    Modify_reject1Bt = tk.Button(modifyroot,image=_Modify_reject1)
                    Modify_reject1Bt["command"] = lambda : fnc.std.modify.birth_org(False)
                    Modify_reject1Bt['cursor'] = 'hand2'
                    Modify_reject1Bt.place(x=350,y=117)

                    Modify_birth_Entry_font = Font(family = '맑은 고딕', size = 23)
                    Modify_birth_Entry = tk.Entry(modifyroot,relief="solid",bd=3)
                    Modify_birth_Entry.insert(0,StudentList[datas.std.header[0]][std_selected_index])
                    Modify_birth_Entry["width"] = 12
                    Modify_birth_Entry["insertwidth"] = 4
                    Modify_birth_Entry["font"] = Modify_birth_Entry_font
                    Modify_birth_Entry.place(x=125,y=125)

                    modifyroot.update()
                def Bt2():
                    global modifyroot,_Modify_confirm2,Modify_confirm2Bt,_Modify_reject2,Modify_reject2Bt,Modify_Name_Entry
                    _Modify_confirm2= fnc.img("sources/imgs/buttons/confirm.png",root=modifyroot)
                    Modify_confirm2Bt = tk.Button(modifyroot,image=_Modify_confirm2)
                    Modify_confirm2Bt["command"] = lambda : fnc.std.modify.name_org(True)
                    Modify_confirm2Bt['cursor'] = 'hand2'
                    Modify_confirm2Bt.place(x=415,y=197)

                    _Modify_reject2= fnc.img("sources/imgs/buttons/cancel.png",root=modifyroot)
                    Modify_reject2Bt = tk.Button(modifyroot,image=_Modify_reject2)
                    Modify_reject2Bt["command"] = lambda : fnc.std.modify.name_org(False)
                    Modify_reject2Bt['cursor'] = 'hand2'
                    Modify_reject2Bt.place(x=350,y=197)

                    Modify_Name_Entry_font = Font(family = '맑은 고딕', size = 23)
                    Modify_Name_Entry = tk.Entry(modifyroot,relief="solid",bd=3)
                    Modify_Name_Entry.insert(0,StudentList[datas.std.header[2]][std_selected_index])
                    Modify_Name_Entry["width"] = 12
                    Modify_Name_Entry["insertwidth"] = 4
                    Modify_Name_Entry["font"] = Modify_Name_Entry_font
                    Modify_Name_Entry.place(x=125,y=205)

                    modifyroot.update()
                def Bt3():
                    global modifyroot,_Modify_confirm3,Modify_confirm3Bt,Modify_reject3Bt,_Modify_reject3,Modify_stdnum_Entry
                    _Modify_confirm3= fnc.img("sources/imgs/buttons/confirm.png",root=modifyroot)
                    Modify_confirm3Bt = tk.Button(modifyroot,image=_Modify_confirm3)
                    Modify_confirm3Bt["command"] = lambda : fnc.std.modify.stdnum_org(True)
                    Modify_confirm3Bt['cursor'] = 'hand2'
                    Modify_confirm3Bt.place(x=875,y=120)

                    _Modify_reject3= fnc.img("sources/imgs/buttons/cancel.png",root=modifyroot)
                    Modify_reject3Bt = tk.Button(modifyroot,image=_Modify_reject3)
                    Modify_reject3Bt["command"] = lambda : fnc.std.modify.stdnum_org(False)
                    Modify_reject3Bt['cursor'] = 'hand2'
                    Modify_reject3Bt.place(x=810,y=120)

                    Modify_stdnum_Entry_font = Font(family = '맑은 고딕', size = 23)
                    Modify_stdnum_Entry = tk.Entry(modifyroot,relief="solid",bd=3)
                    Modify_stdnum_Entry.insert(0,StudentList[datas.std.header[1]][std_selected_index])
                    Modify_stdnum_Entry["width"] = 12
                    Modify_stdnum_Entry["insertwidth"] = 4
                    Modify_stdnum_Entry["font"] = Modify_stdnum_Entry_font
                    Modify_stdnum_Entry.place(x=585,y=125)

                    modifyroot.update()
            def add_student():
                global addstdroot,stdadd_gender

                stdadd_gender = None

                def off():
                    global addstdroot
                    addstdroot.destroy()
                addstdroot = tk.Toplevel()
                addstdroot.protocol('WM_DELETE_WINDOW',off)

                addstdroot.title("학생 등록 / "+title)
                addstdroot.iconbitmap(path('sources/icon.ico'))
                geometry = '%dx%d+%d+%d' % (960,360,(1920-960)/2, (1080-360)/2)
                addstdroot.geometry(geometry)
                addstdroot.resizable(False,False)
                addstdroot.lift()
                addstdroot.bind(
                    "<Escape>",
                    lambda event : off()
                )
                addstdroot.bind(
                    "<Return>",
                    lambda event : fnc.Null()
                )
                addstdroot.grab_set()

                windows.student_management.additional_std.add_student_widget()
            def add_student_widget():
                global _addstdbg,addstdbg,addstd_saveBt,_addstd_save,addstd_cancelBt,_addstd_cancel,addstd_birth_Entry,addstd_Name_Entry,addstd_stdnum_Entry,_addstd_man,addstd_man,\
                addstd_woman,_addstd_woman

                _addstdbg = fnc.img("sources/imgs/bg/stdaddrootbg.png",root=addstdroot)
                addstdbg = tk.Label(addstdroot,image=_addstdbg)
                addstdbg.place(x=-2,y=0)

                _font = Font(family = '맑은 고딕', size = 23)
                addstd_birth_Entry = tk.Entry(addstdroot,relief="solid",bd=3)
                addstd_birth_Entry["width"] = 20
                addstd_birth_Entry["insertwidth"] = 4
                addstd_birth_Entry["font"] = _font
                addstd_birth_Entry.place(x=125,y=125)

                addstd_Name_Entry = tk.Entry(addstdroot,relief="solid",bd=3)
                addstd_Name_Entry["width"] = 20
                addstd_Name_Entry["insertwidth"] = 4
                addstd_Name_Entry["font"] = _font
                addstd_Name_Entry.place(x=125,y=205)

                addstd_stdnum_Entry = tk.Entry(addstdroot,relief="solid",bd=3)
                addstd_stdnum_Entry["width"] = 20
                addstd_stdnum_Entry["insertwidth"] = 4
                addstd_stdnum_Entry["font"] = _font
                addstd_stdnum_Entry.place(x=585,y=125)

                _addstd_man = fnc.img("sources/imgs/buttons/unselect.png",root=addstdroot)
                addstd_man = tk.Button(addstdroot,image=_addstd_man)
                addstd_man["command"] = lambda:fnc.std.add_gender(0)
                addstd_man['cursor'] = 'hand2'
                addstd_man.place(x=650,y=190)

                _addstd_woman = fnc.img("sources/imgs/buttons/unselect.png",root=addstdroot)
                addstd_woman = tk.Button(addstdroot,image=_addstd_woman)
                addstd_woman["command"] = lambda:fnc.std.add_gender(1)
                addstd_woman['cursor'] = 'hand2'
                addstd_woman.place(x=800,y=190)
                
                _addstd_save= fnc.img("sources/imgs/buttons/regist.png",root=addstdroot)
                addstd_saveBt = tk.Button(addstdroot,image=_addstd_save)
                addstd_saveBt["command"] = fnc.std.add_save
                addstd_saveBt['cursor'] = 'hand2'
                addstd_saveBt.place(x=675,y=275)

                _addstd_cancel= fnc.img("sources/imgs/buttons/pddeny.png",root=addstdroot)
                addstd_cancelBt = tk.Button(addstdroot,image=_addstd_cancel)
                addstd_cancelBt["command"] = fnc.std.exit
                addstd_cancelBt['cursor'] = 'hand2'
                addstd_cancelBt.place(x=30,y=275)
        def stock_income():
            global root
            fnc.stock.TreeBox(stockLogList)
    class calculation:
        pass


if __name__ == "__main__":
    # windows.main.init()
    # datas.init(
    # print(datas.stock.search_timeline(19200101,30400202))

    fnc.stock.graph("all",[])