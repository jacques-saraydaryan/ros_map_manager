import psycopg2
#import gdal
import os
script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in


class PostGisDao:
    POSTGRES_USER = "postgres"
    POSTGRES_USER_PWD = "astro4Student"
    POSTGRES_DB_NAME ="world_mng_db"
    POSTGRES_IP="172.17.0.2"
    POSTGRES_PORT="5432"
    CONFIG_PATH="../../config"
    CONFIG_FILE_NAME="schemas.sql"
    
    def __init__(self,host=POSTGRES_IP,
                    port=POSTGRES_PORT,
                    db_name=POSTGRES_DB_NAME,
                    user=POSTGRES_USER_PWD,
                    pwd=POSTGRES_USER_PWD,
                    re_create_db=False):
        self.configure()

        if re_create_db:
            #Get relative file path
            abs_file_path = os.path.join(script_dir, self.CONFIG_PATH + "/"+self.CONFIG_FILE_NAME)
            #Ask DB Schema creation
            self.create_db(abs_file_path)

    def configure(self):
        self.connection = psycopg2.connect(host=self.POSTGRES_IP, 
                                           port=self.POSTGRES_PORT,
                                           database=self.POSTGRES_DB_NAME,
                                           user=self.POSTGRES_USER, 
                                           password=self.POSTGRES_USER_PWD)
        self.cursor = self.connection.cursor()

    def create_db(self,sql_file_path):
        # load table schema
        self._execute(open(sql_file_path, "r").read(),commit=True)

    def select_request(self, sql_request, typeObj='Object'):
        data_list=[]
        try:
            if typeObj == 'Object':
                std_cmd="select id, type, ST_x(coordinate), ST_y(coordinate), ttl, type_name, confidence, orient_x, orient_y, orient_z, orient_w,update_date,json_payload from object;"
                self._execute(std_cmd)
                for id,type,x,y,ttl,type_name,confidence,orient_x,orient_y,orient_z,orient_w,update_date,json_payload in self.cursor:
                   data={'id':id,'type':type,'x':x,'y':y,'ttl':ttl,'type_name':type_name,'confidence':confidence,'orient_x':orient_x,'orient_y':orient_y,'orient_z':orient_z,'orient_w':orient_w,'update_date':update_date,'json_payload':json_payload}
                   data_list.append(data)
            else:
                self._execute(sql_request)
                for obj in self.cursor:
                    data={}
                    for i in range(0,len(obj)):
                        current_column_name = self.cursor.description[i].name
                        data[current_column_name]=obj[i]
                    data_list.append(data)
        except Exception as err:
            raise Exception('PostGisDao', err)
        return data_list


    def add_geo_object(self,id,type,x,y,z,ttl,type_name="",confidence="0.0",orient_x=0,orient_y=0,orient_z=0,orient_w=1,json_payload="{}"):
        std_cmd="INSERT INTO object (id,type,coordinate,ttl,type_name,confidence,orient_x,orient_y,orient_z,orient_w,json_payload) VALUES ('%s','%s',ST_SetSRID(ST_MakePoint(%s,%s, %s),4326),%s,'%s',%s,%s,%s,%s,%s,'%s')"%(id,type,x,y,z,ttl,type_name,confidence,orient_x,orient_y,orient_z,orient_w,json_payload)
        print(std_cmd)
        self._execute(std_cmd,commit=True)

    def get_obj_in_range(self,x,y,r):
        std_cmd="select id,type,ST_x(coordinate),ST_y(coordinate), ttl, type_name, confidence, orient_x, orient_y, orient_z, orient_w,update_date,json_payload from object where ST_DWithin(coordinate, ST_SetSRID(ST_Point(%s, %s), 4326), %s);"%(x,y,r)
        #print(std_cmd)
        self._execute(std_cmd)
        data_list=[]
        for id,type,x,y,ttl,type_name,confidence,orient_x,orient_y,orient_z,orient_w,update_date,json_payload in self.cursor:
            data={'id':id,'type':type,'x':x,'y':y,'ttl':ttl,'type_name':type_name,'confidence':confidence,'orient_x':orient_x,'orient_y':orient_y,'orient_z':orient_z,'orient_w':orient_w,'update_date':update_date,'json_payload':json_payload}
            data_list.append(data)
        return data_list

    def get_all_object_in_room(self,room_name):
        #std_cmd="select object.id,object.type,ST_x(object.coordinate),ST_y(object.coordinate), object.ttl, '\
        #    object.type_name, object.confidence,  object.orient_x, object.orient_y, object.orient_z, object.orient_w '\
        #    from object join room on ST_WITHIN(object.coordinate, room.poly) where room.room='%s';"%(room_name);
        std_cmd="select object.id,object.type,ST_x(object.coordinate),ST_y(object.coordinate), object.ttl, object.type_name, object.confidence,  object.orient_x, object.orient_y, object.orient_z, object.orient_w, object.update_date, object.json_payload from object join room on ST_WITHIN(object.coordinate, room.poly) where room.room='%s';"%(room_name);
        #print(std_cmd)
        self._execute(std_cmd)
        data_list=[]
        for id,type,x,y,ttl,type_name,confidence,orient_x,orient_y,orient_z,orient_w,update_date, json_payload in self.cursor:
            data={'id':id,'type':type,'x':x,'y':y,'ttl':ttl,'type_name':type_name,'confidence':confidence,'orient_x':orient_x,'orient_y':orient_y,'orient_z':orient_z,'orient_w':orient_w,'update_date':update_date,'json_payload':json_payload}
            data_list.append(data)
        return data_list


    def load_raster_into_PostGIS(self, image_name):
       with open(image_name, 'rb') as f:
           self.cursor.execute("INSERT INTO map_raster(map) VALUES (ST_FromGDALRaster(%s))", (f.read(),))
           self.connection.commit()

    def _execute(self,request,commit=False):
        """
        Encapsulate request execution to apply rollback in case of error
        - @param request: sqt request to execute
        - @param commit: enable commit after request execution
        """
        try:
            self.cursor.execute(request)
            if(commit):
                self.connection.commit()
        except Exception as err:
             self.connection.rollback()
             raise Exception('PostGisDao', err)


if __name__ == '__main__':
    # True means data base is re created
    dao=PostGisDao(re_create_db=True)

    try:
        #Add Obj1
        dao.add_geo_object(1,"Object",2,2,0,50,type_name="CHAIR")    
        #Add Obj2
        dao.add_geo_object(2,"Object",2,2.5,0,50,type_name="TABLE")    
        #Add Obj3
        dao.add_geo_object(3,"Object",2.5,2,0,50,type_name="COUCH")
    
        #Add Obj4
        dao.add_geo_object(4,"Object",0.5,0.5,0,50,type_name="CHAIR") 
    
        #load converted map geo tiff to db
        abs_geotiff_file_path = os.path.join(script_dir,"../tmp/map.gtiff")
        dao.load_raster_into_PostGIS(abs_geotiff_file_path)

    except Exception as err:
        print(err)
        
    # get object in a room
    data= dao.get_all_object_in_room('Kitchen')
    print(data)
    print("\n")
    # get object in range 
    data =dao.get_obj_in_range(0.5,0.5,2.25)
    print(data)
    print("\n")

    # get all object custom request
    data =dao.select_request("select * from object;")
    print(data)
    print("\n")

    data =dao.select_request("select * from object;",typeObj='Other')
    print(data)



#cursor.execute("INSERT INTO object (id,type,coordinate,ttl) VALUES ('test','chair','(1.23, 4.56)',100)");
#cursor.execute("DROP TABLE IF EXISTS blocks")
#cursor.execute("CREATE TABLE blocks (id SERIAL PRIMARY KEY, fips VARCHAR NOT NULL, pop BIGINT NOT NULL, outline GEOGRAPHY)")
#cursor.execute("CREATE INDEX block_index ON blocks USING GIST(outline)")
#connection.commit()
#cursor.execute("DELETE FROM blocks")
#cursor.execute("ALTER TABLE blocks ADD COLUMN centroid GEOGRAPHY")