from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.utils import platform
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock


from datetime import datetime

import threading
import json
import requests
import os

from getmac import get_mac_address as gma


Builder.load_string(
'''
#:import ZBarCam kivy_garden.zbarcam.ZBarCam
<CameraClick>:
    
    BoxLayout:
        orientation: 'vertical'
        BoxLayout:
            orientation: 'horizontal'        
            size_hint_y: None
            height: '48dp'
                    
            Button:
                id : back_login    
                text: 'login'
                on_press: root.back_to_login()
            Button:
                text: 'Sync'
                on_press: root.to_sync()                    
                            
                    
        Label :
            id : code
            text : 'No Code'
            size_hint_y: None
            height: '48dp'
                
        ZBarCam:
            id: zbarcam                                    
            canvas.before:
                PushMatrix
                Rotate:
                    angle: 0
                    origin: self.center
            canvas.after:
                PopMatrix
            on_symbols: root.scan_barcode()
            
                

        Label :
            id : Clabel
            
            size: self.texture_size[0], 50                    
            text: ', '.join([str(symbol) for symbol in zbarcam.symbols])
            size_hint_y: None
            height: '48dp' 

        Button:
            id : capture_button
            text: 'Capture'
            size_hint_y: None
            height: '48dp'
            on_release: root.start_scanning()
                                                    
        Button:
            id : save
            text: 'Save'
            size_hint_y: None
            height: '48dp'
            on_press: root.save_barcode()
            
                    
<LoginScreen>:
    BoxLayout:
        orientation: 'vertical'
        Label:
            id: login_lab        
            text: 'Login Screen'
            size_hint_y: None
            height: '48dp'
                    
        TextInput:
            id: username_input
            hint_text: 'Enter User ID'
            input_type: 'number'                 
            size_hint_y: None
            height: '48dp'

        Button:
            id : login_btn        
            text: 'Login'
            size_hint_y: None
            height: '48dp'
            on_press: root.login()           

<SyncScreen>:
    BoxLayout:
        orientation: 'vertical'
        size_hint: None ,None           
        pos_hint: {'center_x': 0.5 , 'center_y': 0.5}
                                    
        Button:
            id: clear
            size_hint_y: None
            height: '48dp'                    
            text: 'Clear'
            on_press: root.clear_data()

        Button:
            id : back_scan
            size_hint_y: None
            height: '48dp'                    
            text: 'Scan'
            on_press: root.back_to_scan()
                        

        Label:
                    
            id: countlabel        
            text: 'Count'
            size_hint: None,None
            height: '48dp'

        Label:
            
            id: count        
            text: '0'
            size_hint: None,None
            height: '48dp'

        Button:
                                
            id : sync_btn        
            text: 'Sync'
            size_hint_y: None
            height: '48dp'
            on_press: root.sync_data()
                
        Label:
            
            id: sylabel        
            text: ' '
            size_hint: None,None
            height: '48dp'

                            
                                                            
''')


class LoginScreen(Screen):

    def check_thread_status(self, dt):
        if self.t1.is_alive():
            pass
        else:
            
            Clock.unschedule(self.check_thread_status)
            if self.lstatus:
                self.manager.get_screen('scan').ids.Clabel.text = ' '
                self.manager.get_screen('scan').ids.code.text = f'Welcome, {self.manager.code}'    
                #self.manager.get_screen('scan').ids.zbarcam.play = True
                self.manager.current = 'scan'

    def login(self):
        #self.t1 = None
        self.lmessg = ' '    
        self.lstatus = False    
        username = self.ids.username_input.text
        self.L_label = self.ids['login_lab']
        self.login_button = self.ids['login_btn']

        if username :
             
            self.user = username
            
                
            
            #self.get_db()
            
            self.t1 = threading.Thread(target = self.get_db)
            self.t1.start()
            Clock.schedule_interval(self.check_thread_status, 1)

    def get_db(self):

        try:
            self.L_label.text = 'Pls wait connecting to DB ....'
            self.login_button.disabled = True

            try :
                self.user = int(self.user)
                code = self.user
                 
            except:
                self.lmessg = 'Username Should be Numerical'
                self.L_label.text = self.lmessg
                return
                
                

            data = {'login':code}
            print(data)
           
            url  = 'https://fastapiqr-1-o8386309.deta.app/get_data/'

            res =  requests.get(url, params=data)
            
            if res.ok:
                print(res.json())
                result = res.json()
                
# Api check             
                code  = result['code']
                
                if code == self.user:
                    self.manager.code = code
                   
                    self.lstatus = True
                    self.lmessg = 'Data Matches'
                    return
                
                                             
                     

                else : 
                    self.lmessg = 'No User ID found'
                    self.L_label.text = self.lmessg    

            else :
                self.lmessg = "Error in Response"
                self.L_label.text = self.lmessg


        except Exception as e:
            print(e)
            
            self.lmessg = "Error in Response"
            print('error1')
            self.L_label.text = self.lmessg
            
            
        finally : 

            #self.manager.get_screen('scan').ids.Clabel.text = ' '
    
            self.login_button.disabled = False
            return
                    

class CameraClick(Screen):

    def start_scanning(self):

        self.zbarcam = self.ids.zbarcam
        self.ch = 0
        Clock.schedule_interval(self.check_start, 0.1)

    def check_start(self,dt):

        self.zbarcam.start()
        self.ch = self.ch + 1
        if  self.ch == 2 :
            Clock.unschedule(self.check_start)

    def scan_barcode(self):
        self.zbarcam = self.ids['zbarcam'] 

        self.zbarcam.stop()
        newdata = None
        try : 
            for symbol in self.zbarcam.symbols:
                qrtype = symbol.type
                data = symbol.data
                n = data.decode('utf-8')
                newdata = {'type' : qrtype , 'value' : n}
                break
        except:
            print('error in loop')        
            newdata = None
            
        
        self.manager.currdata = newdata      

    def save_barcode(self):
        self.label = self.ids['Clabel']
        self.save_button = self.ids['save']
        self.zbarcam = self.ids['zbarcam']
        #self.capture_button = self.ids['capture']
        
        if self.manager.currdata : 
            
            self.label.text = 'Pls wait saving ....'    
            self.save_data()
            # t1 = threading.Thread(target = self.save_data)
            # t1.start()
            

        else :
            self.label.text = 'No Data to Save'
            self.manager.currdata = None   

    def back_to_login(self):
        self.manager.get_screen('login').ids.login_lab.text = 'Login'
        self.manager.current = 'login'
        #self.zbarcam.play = False
        
    def save_data(self):
        try:        
            self.capture_button = self.ids['capture_button']
            self.save_button.disabled = True
            self.capture_button.disabled = True
            new_data = self.manager.currdata


            try:
                fname = self.manager.file_path
                
                print('path found')
                self.label.text = 'path found'     
                
            except:
                self.label.text = 'error in file path'
                print('error in file path')
                self.manager.currdata = None
                self.save_button.disabled = False
                self.capture_button.disabled = False

                return
            
            try : 
                print('Done till 1 ')
                try :                 
                    with open(fname, 'r') as f:
                        
                        existing_data = json.load(f)
                        print('Done 2')
                except : 
                    existing_data = []
                    with open(fname, 'w') as f:
                    
                        json.dump(existing_data, f)
                    print('Done 3')    

                # Append new data to the existing data
                current_datetime = datetime.now()
                formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
                formatted_datetime = str(formatted_datetime)
                new_data.update({'login_code':self.manager.code,'scan_time':formatted_datetime,'mac_add' : self.manager.mac_add})
                
                existing_data.append(new_data)

                print(type(existing_data))
                print(len(existing_data))
                
                # Write the updated data back to the file
                with open(fname, 'w') as f:
                    
                    json.dump(existing_data, f)

                print('Data Save Succefully')
                self.label.text = 'Data Save Succefully'


            except:

                self.label.text = 'Error in saving'

                print('Error in saving')

        except:
            pass
        finally :
            self.manager.currdata = None
            self.save_button.disabled = False
            self.capture_button.disabled = False
                                      
    def to_sync(self):
        count = '0'
        
        #self.manager.get_screen('sync').ids.tmac.text = f'{mac}'
        self.zbarcam = self.ids['zbarcam']
        #self.zbarcam._camera = None
        
        try : 
            fname = self.manager.file_path
            
            

                
            with open(fname, 'r') as f:
                
                existing_data = json.load(f)

            count = len(existing_data) 

            count = str(count)
        except:
            pass
        self.manager.currdata = None    
        self.manager.get_screen('sync').ids.count.text = count
        self.manager.get_screen('sync').ids.sylabel.text = ' '
        self.manager.current = 'sync'       


class SyncScreen(Screen):
    '''    
    def check_thread_status(self, dt):
        if self.t1.is_alive():
            print("Thread is running...")
        else:
            print("Thread has finished")
            Clock.unschedule(self.check_thread_status)'''
    
    def sync_data(self):
        self.existing_data = None
        l = None
        
        self.syl = self.ids['sylabel']
        

        try:
                    
            fname = self.manager.file_path
                
            
        except:
            self.syl.text = 'Error in path'        
        
        try:
            with open(fname, 'r') as f:

                self.existing_data = json.load(f)
                l = len(self.existing_data)
        except:
            
            self.syl.text = 'Error in opening file'

        if self.existing_data and l > 0:
            try :
                self.syl.text = 'pls wait Connecting DB'    
                self.t1 = threading.Thread(target = self.upload_data)
                self.t1.start()
                Clock.schedule_interval(self.check_thread_status, 1)

                #t1.join()
                
                # if self.manager.synstatus ==True:
                #     self.clear_data()

            except:
                self.syl.text = 'Error in thread'   

        else:
            self.syl.text = 'No Data to sync'
                                            
    def upload_data(self):
        
        try:
            self.syl = self.ids['sylabel']
            self.sybtn = self.ids['sync_btn']
            self.clrbtn = self.ids['clear']
            self.btsc = self.ids['back_scan']   
            
            self.sybtn.disabled = True                               
            self.clrbtn.disabled = True                               
            self.btsc.disabled = True                               
            
            data = self.existing_data
            url = 'https://fastapiqr-1-o8386309.deta.app/save_data/'
            
            self.manager.synstatus = False

# very IMP Check API status                         
# Also dicuss for loop and db rollback

            for x in data:
                try:
                    res = requests.post(url, params=x)
                
                    if res.ok:
                        print(res.json())
                        result = res.json()
                        self.manager.synstatus = result['status']
                        message = result['message']
                    else :
                        self.syl.text = 'Error in Response'    
                        self.manager.synstatus = False
                        message = ' '

                except:
                    self.syl.text = 'Error in Response'
                    message = ' '
                    self.manager.synstatus = False
                                                
            self.syl.text = message
            if self.manager.synstatus == True:
                self.clear_data()                            

        except:
            pass
        
        finally:
            self.sybtn.disabled = False                               
            self.clrbtn.disabled = False                               
            self.btsc.disabled = False
            return
                                           
    def back_to_scan(self):
        self.manager.get_screen('scan').ids.Clabel.text = ' ' 
        self.manager.current = 'scan'

    def clear_data(self):
 
        clear = []       

        try :
            self.syl = self.ids['sylabel']
            self.sybtn = self.ids['sync_btn']
            self.clrbtn = self.ids['clear']
            self.btsc = self.ids['back_scan']
            
            self.count = self.ids['count']  
        
            self.sybtn.disabled = True                               
            self.clrbtn.disabled = True                               
            self.btsc.disabled = True                               

            try:

                fname = self.manager.file_path
                
                print('changed')                

            except:
                self.syl.text = 'Error in path'        

            try:
                with open(fname, 'w') as f:

                        
                    json.dump(clear, f)
                    print('Data clear')
                
                self.syl.text = 'Data clear successfully !'
                print('Data clear successfully !')
                 
                if self.manager.synstatus == True:
                    
                    self.syl.text = 'Data saved successfully!'
                
                
                self.count.text = '0'
                self.manager.synstatus = False    

            except:
                print('hello')
                self.syl.text = 'Error in File'
        except:
            pass

        finally:
            self.sybtn.disabled = False                               
            self.clrbtn.disabled = False                               
            self.btsc.disabled = False                               
                

class MyScreenManager(ScreenManager):
    pass


class TestCamera(App):

    def build(self):
        

        mac_add = 'Not Found'
        file_path = 'Not_Found'  

        if platform =='android':
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.READ_EXTERNAL_STORAGE,Permission.WRITE_EXTERNAL_STORAGE,Permission.CAMERA,Permission.INTERNET,Permission.ACCESS_WIFI_STATE,Permission.READ_PHONE_STATE])
            
        try : 
            if platform =='android':

                # getting wifi_mac                    
                try:
                    from jnius import autoclass
                    mac_add = ""

                    NetworkInterface = autoclass('java.net.NetworkInterface')

                    interfaces = NetworkInterface.getNetworkInterfaces()

                    while interfaces.hasMoreElements():
                        interface = interfaces.nextElement()
                        if not interface.isLoopback() and not interface.isVirtual():
                            mac_bytes = interface.getHardwareAddress()
                            if mac_bytes is not None:
                                mac_add = ':'.join('{:02x}'.format(byte) for byte in mac_bytes)
                                break                
                except :
                    mac_add = 'Not found'



                # getting file_path    
                try:
                    folder_name = 'qrscan'
                    file_name = 'demo.json'

                    from jnius import autoclass
                    from os.path import join
                    Environment = autoclass('android.os.Environment')
                    directory = join(Environment.getExternalStorageDirectory().getAbsolutePath(), folder_name)
                    
                    # Create the folder if it doesn't exist
                    File = autoclass('java.io.File')

                    folder = File(directory)

                    if not folder.exists():
                        folder.mkdirs()
                    
                    file_path = join(directory, file_name)

                    # Create the file if it doesn't exist
                    file = File(file_path)
                    if not file.exists():
                        file.createNewFile()                            

                except:
                    file_path = ' Not Found'
            
            else :
                #getting wifi
                try : 
                    mac_add = str(gma())
                    print(mac_add)        
                except :
                    mac_add = 'Not found'

                #getting file_path
                try : 
                    folder_path ='./otherAPP'
                    file_name = 'demo.json'
                
                    file_path = os.path.join('./otherAPP','demo.json')
                except:
                    pass    

        except : 
            pass            

        screen_manager = MyScreenManager()
        screen_manager.add_widget(LoginScreen(name='login'))
        screen_manager.add_widget(CameraClick(name='scan'))
        screen_manager.add_widget(SyncScreen(name='sync'))
        
        screen_manager.currdata = None
        screen_manager.mac_add = str(mac_add)
        screen_manager.code = None
        screen_manager.file_path = file_path
        screen_manager.synstatus = False

        return screen_manager

if __name__ == '__main__':

    TestCamera().run()