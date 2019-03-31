

import datetime

import pymysql


class sqlHelper(object):
    def  __init__(self,host,port,user,passwd,db,table):
        self.host = host
        self.port = port
        self.user = user
        self.password = passwd
        self.db = db
        self.table = table
        self.connect_state = False
    def connect_mysql(self):
        try:
            self.conn = pymysql.connect(host=self.host,port=self.port,user=self.user,passwd=self.password,db=self.db,charset='utf8')
            self.cursor = self.conn.cursor()
            self.connect_state = True
            print('sql connect ok')
        except:
            print('sql connect error')
    def close_mysql(self):
        self.conn.close()
        self.connect_state = False
    def query(self):
        if self.connect_state:
            sql = "select * from "+self.table+";"
            try:
                self.cursor.execute(sql)
                # row = self.cursor.fetchone()
                results = self.cursor.fetchall()
                provinceQuantity = 0
                for row in results:
                    provinceQuantity += 1
                    print(row)

                print(provinceQuantity)
            except:
                print("query failed")
    def insert_mysql(self,arg,value):
        if self.connect_state:
            table = self.table
            try:
                self.cursor.execute("INSERT INTO "+table+"(" + arg + ") VALUE(" + value + ");")
                self.conn.commit()
                print('insert ok')
            except:
                print("insert failed")

    def insert_noarg_mysql(self,value):
        if self.connect_state:
            table = self.table
            try:
                self.cursor.execute("INSERT INTO "+table+" VALUE(" + value + ");")
                self.conn.commit()
                print('insert ok')
            except:
                print("insert failed")

    def update_mysql(self,value,key):
        if self.connect_state:
            table = self.table
            try:
                self.cursor.execute("UPDATE "+table+" set "+value+" where "+key+";")
                self.conn.commit()
                print('update ok')
            except:
                self.conn.rollback()
                print("update failed")

    def delete_row_mysql(self, value, key):
        if self.connect_state:
            table = self.table
            try:
                self.cursor.execute("DELETE FROM " + table + " WHERE " + key + " = " + value + ";")
                self.conn.commit();
                print("delete ok")
            except:
                self.conn.rollback()
                print("delete failed")

    def creat_mysql(self):

        sql = """CREATE TABLE tractor (
        id int auto_increment,
        tractor_id int ,
        year int,
        month SMALLINT ,
        day SMALLINT ,
        hour SMALLINT ,
        minute SMALLINT ,
        second SMALLINT ,
        mus int,
        plateNum  CHAR(20),
        carType CHAR(10),
        serialNum int ,
        driver CHAR(10),
        phone CHAR(20),
        speed int ,
        rotateSpeed int ,
        avgEconomy int, 
        gasMassPercent int ,
        waterTemp int, 
        leftLamp SMALLINT ,
        rightLamp SMALLINT ,
        highBeam SMALLINT ,
        lowBeam SMALLINT ,
        gasLamp SMALLINT,  
        engineHitchLamp SMALLINT  ,
        waterTempLamp SMALLINT ,
        oilLamp SMALLINT ,
        batteryLamp SMALLINT  ,
        parkingLamp SMALLINT ,
        parkingHitchLamp SMALLINT ,
        longitude DOUBLE ,
        latitude DOUBLE,
        altitude DOUBLE ,
        primary key(id,tractor_id,year,month,day,hour,minute,second,mus))default charset=utf8;"""

        mapProvince = """
        CREATE TABLE map_province(
        provinceID int,
        provinceName CHAR(10),
        provinceZoom int,
        provinceLongitude DOUBLE,
        provinceLatitude DOUBLE
        )charset=utf8;
        """

        mapCity = """
        CREATE TABLE map_city(
        cityID int,
        cityName CHAR(10),
        cityZoom int,
        cityLongitude DOUBLE,
        cityLatitude DOUBLE
        )charset=utf8;
        """

        mapTractor = """
        CREATE TABLE map_tractor(
        serialNum int,
        longitude DOUBLE,
        latitude DOUBLE
        )charset=utf8;
        """

        warning = """
        CREATE TABLE warning(
        serial int,
        time int,
        id int,
        level int,
        title CHAR(20),
        content CHAR(100)
        )charset=utf8;
        """

        statistical = """
        CREATE TABLE statistical(
        id int,
        time int,
        frequency int,
        place CHAR(20),
        water_temp int,
        motor int,
        machine_oil int,
        battery int,
        fuel int,
        wash_water int
        )charset=utf8;
        """
        try:
            self.cursor.execute(warning)
            print("creat ok")
        except:
            print("creat fail")

    def add_map_information(self, kind, id, part1, part2, part3, part4):
        information = self.get_map_information()
        if kind == "province":
            for i in information['provinceID']:
                if id == i:
                    return
            sql = "INSERT INTO map_province(provinceID, \
                provinceName,provinceZoom,provinceLongitude, \
                provinceLatitude) \
                VALUES('%s', '%s', %s, '%s', '%s')" % (id, part1, part2, part3, part4)

        elif kind == "city":
            for i in information['cityID']:
                if id == i:
                    return
            sql = "INSERT INTO map_city(cityID, \
                cityName,cityZoom,cityLongitude, \
                cityLatitude) \
                VALUES('%s', '%s', %s, '%s', '%s')" % (id, part1, part2, part3, part4)

        elif kind == "tractor":
            for i in information['serialNum']:
                if id == i:
                    return
            sql = "INSERT INTO map_tractor(serialNum, \
                longitude, \
                latitude) \
                VALUES('%s', '%s', %s)" % (id, part1, part2)

        else:
            return

        self.cursor.execute(sql)
        self.conn.commit()

    def delete_map_information(self, kind, id):
        if kind == "province":
            sql = "DELETE FROM map_province WHERE provinceID = %s" % id
        elif kind == "city":
            sql = "DELETE FROM map_city WHERE cityID = %s" % id
        elif kind == "tractor":
            sql = "DELETE FROM map_tractor WHERE serialNum = %s" % id
        else:
            return

        self.cursor.execute(sql)
        self.conn.commit()

    def get_map_information(self):
        mapInformation = {}
        provinceID = []
        provinceName = []
        provinceZoom = []
        provinceLongitude = []
        provinceLatitude = []
        cityID = []
        cityName = []
        cityZoom = []
        cityLongitude = []
        cityLatitude = []
        serialNum = []
        tractorLongitude = []
        tractorLatitude = []

        if self.connect_state:
            try:
                sql = "SELECT * FROM map_province;"
                self.cursor.execute(sql)
                results = self.cursor.fetchall()
                mapInformation['provinceQuantity'] = 0
                for row in results:
                    provinceID.append(row[0])
                    provinceName.append(row[1])
                    provinceZoom.append(row[2])
                    provinceLongitude.append(row[3])
                    provinceLatitude.append(row[4])
                    mapInformation['provinceQuantity'] += 1

                mapInformation['provinceID'] = provinceID
                mapInformation['provinceName'] = provinceName
                mapInformation['provinceZoom'] = provinceZoom
                mapInformation['provinceLongitude'] = provinceLongitude
                mapInformation['provinceLatitude'] = provinceLatitude

                sql = "SELECT * FROM map_city;"
                self.cursor.execute(sql)
                results = self.cursor.fetchall()
                mapInformation['cityQuantity'] = 0
                for row in results:
                    cityID.append(row[0])
                    cityName.append(row[1])
                    cityZoom.append(row[2])
                    cityLongitude.append(row[3])
                    cityLatitude.append(row[4])
                    mapInformation['cityQuantity'] += 1

                mapInformation['cityID'] = cityID
                mapInformation['cityName'] = cityName
                mapInformation['cityZoom'] = cityZoom
                mapInformation['cityLongitude'] = cityLongitude
                mapInformation['cityLatitude'] = cityLatitude

                sql = "SELECT * FROM map_tractor;"
                self.cursor.execute(sql)
                results = self.cursor.fetchall()
                mapInformation['tractorQuantity'] = 0
                for row in results:
                    serialNum.append(row[0])
                    tractorLongitude.append(row[1])
                    tractorLatitude.append(row[2])
                    mapInformation['tractorQuantity'] += 1

                mapInformation['serialNum'] = serialNum
                mapInformation['tractorLongitude'] = tractorLongitude
                mapInformation['tractorLatitude'] = tractorLatitude

                return mapInformation

            except:
                print("query failed")

    def add_warning_information(self, time, id, level, title, content):
        information = self.get_warning_information()

        serial = len(information['serial'])
        sql = "INSERT INTO warning(serial, \
            time,id,level, \
            title, content) \
            VALUES('%s', '%s', %s, '%s', '%s', '%s')" % (serial, time, id, level, title, content)
        self.cursor.execute(sql)
        self.conn.commit()

    def delete_warning_information(self, serial):
        information = self.get_warning_information()
        last = len(information['serial']) - 1

        sql = "DELETE FROM warning WHERE serial = %s" % serial
        self.cursor.execute(sql)

        if serial < last:
            sql = "DELETE FROM warning WHERE serial = %s" % last
            self.cursor.execute(sql)
            sql = "INSERT INTO warning(serial, \
                time,id,level, \
                title,content) \
                VALUES('%s', '%s', '%s', '%s', '%s', '%s')" % \
                (serial, information['time'][last], information['id'][last],
                 information['level'][last], information['title'][last], information['content'][last])
            self.cursor.execute(sql)

        self.conn.commit()

    def get_warning_information(self):
        information = {}
        serial = []
        time = []
        id = []
        level = []
        title = []
        content = []

        sql = "SELECT * FROM warning;"
        self.cursor.execute(sql)
        results = self.cursor.fetchall()

        for row in results:
            serial.append(row[0])
            time.append(row[1])
            id.append(row[2])
            level.append(row[3])
            title.append(row[4])
            content.append(row[5])

        information['serial'] = serial
        information['time'] = time
        information['id'] = id
        information['level'] = level
        information['title'] = title
        information['content'] = content

        return information

    def add_statistical_information(self, id, time, frequency, region):

        sql = "INSERT INTO statistical(id, \
                    time,frequency,place) \
                    VALUES('%s', '%s', %s, '%s')" % (id, time, frequency, region)
        self.cursor.execute(sql)
        self.conn.commit()

    def delete_statistical_information(self, id):
        sql = "DELETE FROM statistical WHERE id = %s" % id
        self.cursor.execute(sql)
        self.conn.commit()

    def get_statistical_information(self):
        information = {}
        id = []
        time = []
        frequency = []
        region = []

        sql = "SELECT * FROM statistical;"
        self.cursor.execute(sql)
        results = self.cursor.fetchall()

        for row in results:
            id.append(row[0])
            time.append(row[1])
            frequency.append(row[2])
            region.append(row[3])

        information['id'] = id
        information['time'] = time
        information['frequency'] = frequency
        information['region'] = region

        return information


#test = sqlHelper("localhost",3306,"root","123456","tractor","map_tractor")

#test.connect_mysql()
#test.creat_mysql()


#noarg_value = "null,1124,2019,01,16,16,59,30,7863,\'川A4512\',\'M250-E\',8761238,\'林动\',\'18483655552\',20,3000,75,50,90,1,0,1,0,1,1,1,1,1,1,0,2000,32.6578757370,32.6578757370"
#map_province_value = "0,\'四川省\',7,104.06,30.67"

map_city_value1 = "0,\'甘孜州\',9,101.97,30.05"
map_city_value2 = "1,\'阿坝州\',9,101.70,32.90"
map_city_value3 = "2,\'凉山州\',9,102.27,27.90"
map_city_value4 = "3,\'成都\',10,104.06,30.67"
map_city_value5 = "4,\'达州\',10,107.50,31.22"

map_tractor_value1 = "1,101.97,30.05"
map_tractor_value2 = "15,101.90,30.15"
map_tractor_value3 = "3,101.70,32.90"
map_tractor_value4 = "7,101.50,32.80"
map_tractor_value5 = "6,102.27,27.90"
map_tractor_value6 = "24,104.06,30.67"
map_tractor_value7 = " 48,107.50,31.22"




#test.delete_row_mysql("四川省", "provinceName")
#test.query()
#test.close_mysql()