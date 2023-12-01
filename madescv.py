import csv

f = open("./sources/datas/사용로그.csv",'w',newline='')
rdr = csv.writer(f)
rdr.writerow(['년','월','일','시','분','초','학번','이름','행동','수','잔액','비고'])

# f.close()

f = open("./sources/datas/상품목록.csv",'w',newline='')
rdr = csv.writer(f)
rdr.writerow(['번호','상품명','이미지','가격','재고','누적판매'])
f.close()

# f = open("./sources/datas/사용로그.csv",'r',newline='')
# rd = csv.reader(f)
# for line in rd:
#     print(line)
# f.close()

def add1(_list):
    f = open('sources/datas/사용로그.csv','a', newline='')
    wr = csv.writer(f)
    wr.writerow(_list)
    f.close()


# add1(['2023','10','25','12','32','52','20210','손지형','구매','1','6974','느금마'])

def add2(lst):
    f = open('sources/datas/상품목록.csv','a', newline='')
    wr = csv.writer(f)
    wr.writerow(lst)
    f.close()

# add2(['1','홈런볼','homerunball.png','2000','2','1293'])