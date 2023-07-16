from fastapi import FastAPI
from pydantic import BaseModel
import mysql.connector

import uvicorn

app = FastAPI()

config ={
    'host':"localhost",
    'user':"root",
    'password':"",
    'database':"qr",
    'connect_timeout': 5
}

def save_data(data):
    config ={
    'host':"localhost",
    'user':"root",
    'password':"",
    'database':"qr",
    'connect_timeout': 5
                }
    db = None
    try:
        db = mysql.connector.connect(**config)
        
        try :
            print(data)    
            type = data['type']
            value = data['value']
            mac_add = data['mac_add']
            scan_time = data['scan_time']
            login_code = data['login_code']
            


            q = '''INSERT INTO `t2` VALUES (%s, %s, current_timestamp(), %s, NULL, %s, %s);'''           
            v = (type,value,mac_add,login_code,scan_time)                    

            cursor = db.cursor()
            cursor.execute(q,v)
            print('Executed')
            db.commit()
            print('Commited')

            messg = 'Data saved successfully!'
            status = True        
        
        except: 
            
            messg = 'Error in Query Proceesing'
            status = False
            
        

    except:
        messg = 'Error in connecting DB'
        status = False
    finally :

        if db:
            db.close()
        

    return messg ,status


def get_data(data):
    config ={
    'host':"localhost",
    'user':"root",
    'password':"",
    'database':"qr",
    'connect_timeout': 5
                }
    db = None
    code = None
    status = False
    try:
        db = mysql.connector.connect(**config)
        
        try :

            login_code = data['login_code']
            
            q = '''SELECT * FROM `login_table` WHERE code = %s;'''           
            v = (login_code,)                    

            cursor = db.cursor(dictionary=True)
            cursor.execute(q,v)
            rows = cursor.fetchall()
            print(rows)

            for row in rows:
                code = row['code']
            

            messg = 'Data Got successfully!'
            status = True

            if code ==None:
                messg = 'No User ID found'
                status = False         
        
        except: 
            
            messg = 'Error in Query Proceesing'
            status = False
            
        

    except:
        messg = 'Error in connecting DB'
        status = False
        
    finally :

        if db:
            db.close()
            
        

    return code , messg,status


@app.post("/save_data/")
async def save_1(type:str,value:str,mac_add:str,login_code: int, scan_time: str,android_id:str,imbed:str):
    d = {'type':type,'value':value,'mac_add':mac_add,'login_code':login_code,'scan_time':scan_time,'android_id':android_id,'imbed':imbed}
    
    print (d)
    messg ,status= save_data(d)
    
    response = {'message': messg,'status':status}           

    return response

@app.get("/get_data/")
async def get_1(login: int):
    try:
        d = {'login_code':login} 
        print (d)
        code ,messg,status = get_data(d)
        print(f'{code} , {messg}')
        
    except:
        messg = 'Erorr'
        code = None
    
    response = {'code':code,'message': messg,'status':status}           

    return response

if __name__ == "__main__":
   uvicorn.run("new_api:app", host="192.168.0.52", port=8000, reload=True)