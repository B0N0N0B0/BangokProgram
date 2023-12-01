import configparser as cp

class ini:
    def initing():
        config = cp.ConfigParser()

        config['dat'] = {}
        config['dat']['누적수익'] = "0"
        config['dat']['누적판매'] = "0"
        config['dat']['제품군'] = "문구,간편식,음료,의약,스낵,생필품,전자,미용,이벤트,기타"

        config['dat']['기준년'] = "2023"
        config['dat']['기준월'] = '11'
        return config
    def store(config):
        with open("./sources/datas.ini",'w',encoding='UTF-8') as cf:
            config.write(cf)
    def read():
        config = cp.ConfigParser()
        config.read("./sources/datas.ini",encoding = 'UTF-8')
        return config
    
ini.store(ini.initing())