from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.core.image import Image as CoreImage
from kivy.utils import platform
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock


from PIL import Image
from pyzbar import pyzbar

from datetime import datetime

import threading
import json
import requests
import os

from getmac import get_mac_address as gma


# PythonActivity = autoclass('org.kivy.android.PythonActivity')
# WifiManager = autoclass('android.net.wifi.WifiManager')






Builder.load_string('''
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
                
        Camera:
            id: camera
            resolution: (640, 480)
            play: True
                        
            canvas.before:
                PushMatrix
                Rotate:
                    angle: 0
                    origin: self.center
            canvas.after:
                PopMatrix

        Label :
            id : Clabel
            text : ' '
            size_hint_y: None
            height: '48dp'
                                            
        Button:
            id : capture           
            text: 'Capture Image'
            size_hint_y: None
            height: '48dp'
            on_press: root.scan_barcode()
        
        Button:
            id : save
            text: 'Save'
            size_hint_y: None
            height: '48dp'
            on_press: root.save_db()
                    
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
        pos_hint: {'center_x': 0.5, 'center_y': 0.5}    
        Button:
            id: clear
            size_hint_y: None
            height: '48dp'                    
            text: 'Clear Data'
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
            size_hint: None,None
            height: '48dp'
            on_press: root.sync_data()
                
        Label:
            
            id: sylabel        
            text: ' '
            size_hint: None,None
            height: '48dp'
                
                                                            
''')

class LoginScreen(Screen):
    def login(self):

        username = self.ids.username_input.text
        self.L_label = self.ids['login_lab']
        self.login_button = self.ids['login_btn']
        
        if username :
            self.user = username

            self.L_label.text = 'Pls wait connecting to DB ....'    

            t1 = threading.Thread(target = self.get_db)
            t1.start()

    def get_db(self):
        try:
            self.login_button.disabled = True
            
            code = self.user
            try :
                code = int(code) 
            except:
                self.L_label.text = ' Username Should be Numerical'
                return 

            data = {'login':code}
            print(data)
           
            url  = 'http://192.168.0.52:8000/get_data/'

            res = requests.get(url, params=data)
            
            if res.ok:
                print(res.json())
                result = res.json()
                
                self.L_label.text = result['message']
                
                code  = result['code']
                if code == self.user:
                    self.manager.code = code     
                    self.manager.get_screen('scan').ids.code.text = f'Welcome, {self.manager.code}'

                    print('Hello3') 
                    self.manager.current = 'scan'
                    print('Hello4') 

                    # Pass the username to the ScanScreen
 

            else :
                self.L_label.text = f"Error in Response"
                print('hello')        
                
        except : 
            print('hello2')
            self.L_label.text = 'hello2 '



            
        finally : 
            
            self.login_button.disabled = False
            self.L_label.text = ' '
            self.manager.get_screen('scan').ids.Clabel.text = ' '
        


class CameraClick(Screen):

    def scan_barcode(self):
        '''
        mac_add = 'Not Found'
        imbed = 'NotFound'
        android_id = 'Not_found'   

        if platform =='android':
            # getting PythonActivity
            try :          
                from jnius import autoclass, cast
                
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                
                # getting mac_add
                try:
                    WifiManager = autoclass('android.net.wifi.WifiManager')
                    wifi_manager = cast(WifiManager, PythonActivity.mActivity.getSystemService(PythonActivity.WIFI_SERVICE))
                    wifi_info = wifi_manager.getConnectionInfo()
                    mac_add = wifi_info.getMacAddress()
                    mac_add = str(mac_add)

                except:
                    mac_add = 'Not found'
                
                
                # getting imbed
                try:

                    Context = autoclass('android.content.Context')
                    telephonyManager = cast('android.telephony.TelephonyManager', PythonActivity.mActivity.getSystemService(Context.TELEPHONY_SERVICE))
                    imbed = telephonyManager.getDeviceId()
                except:
                    imbed = 'NotFound'

                # getting android id
                try : 
                    SettingsSecure = autoclass('android.provider.Settings.Secure')
                    content_resolver = PythonActivity.mActivity.getContentResolver()
                    android_id = SettingsSecure.getString(content_resolver, SettingsSecure.ANDROID_ID)
                    android_id = str(android_id)
                except:
                    android_id = 'Not_found'

            except:
                pass

        else :
            try : 
                mac_add = str(gma())
                
            except :
                mac_add = 'Not found' '''

        try :
            
            self.camera = self.ids['camera']
            self.label = self.ids['Clabel']
            self.save_button = self.ids['save']
            self.capture_button = self.ids['capture']

            image_texture = self.camera.texture
            
        except:
            image_texture = None

        if image_texture is not None:
            try :
            # Convert the image texture to a CoreImage
                core_image = CoreImage(image_texture)
                
                # Convert the CoreImage to a NumPy array
                
                #image_array = np.frombuffer(core_image.texture.pixels, dtype=np.uint8)
                
                image_array=Image.frombytes(mode='RGBA',size=core_image.texture.size,data=core_image.texture.pixels)

                # image_array = image_array.reshape((core_image.texture.height, core_image.texture.width, 4))
                # image_array = image_array[..., :3]  # Remove the alpha channel
            
            except :
                self.label.text = "Error in image to array Conversion"

            try :
                # Decode barcodes from the frame
                decoded_list = []
                decoded_list = pyzbar.decode(image_array)
            except :
                self.label.text = 'Error in decoding'

            if decoded_list :
                try :     
                    barcode_data = []
                    
                    # Iterate over the detected barcodes
                    
                    for barcode in decoded_list:
                        
                        # Extract the barcode data
                        barcode_value = barcode.data.decode('utf-8')
                        barcode_type = barcode.type
                    
                        # Add the barcode information to the list
                        barcode_data.append({
                        'value': barcode_value,
                        'type': barcode_type })

                    data = barcode_data[0]
                    value = data['value']

                    print(f'new \n {barcode_data}')
                    self.label.text = f'{value}'
                    
                    self.manager.currdata = data

                except : 
                    self.label.text = 'Error in forloop'    

            else :
                self.manager.currdata = None
                self.label.text = 'No barcode Found'

        else:
            self.currdata = None
            self.label.text = "No image to capture"

    def save_db(self):
        self.label = self.ids['Clabel']
        self.save_button = self.ids['save']
        self.capture_button = self.ids['capture']
        
        

        
        if self.manager.currdata : 
            
            self.label.text = 'Pls wait saving ....'    

            t1 = threading.Thread(target = self.save_data)
            t1.start()
            

        else :
            self.label.text = 'No Data to Save'
            self.manager.currdata = None   

    def back_to_login(self):
        self.manager.get_screen('login').ids.login_lab.text = 'Login'
        self.manager.current = 'login'
        

    def save_data(self):
        try:        
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
                with open(fname, 'r') as f:
                    
                    existing_data = json.load(f)

                # Append new data to the existing data
                current_datetime = datetime.now()
                formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
                formatted_datetime = str(formatted_datetime)
                new_data.update({'login_code':self.manager.code,'scan_time':formatted_datetime,'mac_add' :self.manager.mac_add,'android_id' :self.manager.android_id,'imbed' :self.manager.imbed ,'wifi':self.manager.wifi})
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
        count = 'Not found'
        try : 
            fname = self.manager.file_path
                
            with open(fname, 'r') as f:
                
                existing_data = json.load(f)

            count = len(existing_data) 

            count = str(count)
        except:
            pass

        self.manager.get_screen('sync').ids.count.text = count
        self.manager.get_screen('sync').ids.sylabel.text = ' '
        self.manager.current = 'sync'        



class SyncScreen(Screen):
    def sync_data(self):
        self.existing_data = None
        l = None
        self.status = False
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
                t1 = threading.Thread(target = self.upload_data)
                t1.start()
                t1.join()
                print('hey there')
                if self.status ==True:
                    self.clear_data()

            except:
                self.syl.text = 'Error in thread'   

        else:
            self.syl.text = 'No Data to sync'
            print('No Data to sync')
                                 
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
            url = 'http://192.168.0.52:8000/save_data/'
            
            self.status = False

            for x in data:
                try:
                    res = requests.post(url, params=x)
                
                    if res.ok:
                        print(res.json())
                        result = res.json()
                        self.status = result['status']
                        message = result['message']
                        self.syl.text = message
                        
                    else :
                        self.syl.text = 'Error in Response'    
                except:
                    self.syl.text = 'Error in Response'

                    

            

        except:
            pass
        
        finally:
            self.sybtn.disabled = False                               
            self.clrbtn.disabled = False                               
            self.btsc.disabled = False
                                           
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
        
            self.sybtn.disabled = True                               
            self.clrbtn.disabled = True                               
            self.btsc.disabled = True                               

            try:

                fname = self.manager.file_path                

            except:
                self.syl.text = 'Error in path'        
            try:
                with open(fname, 'w') as f:

                    json.dump(clear, f)
                
                self.syl.text = 'Data clear successfully !'

                if self.status == True:
                    
                    self.syl.text = 'Data saved successfully!'
                
                
                self.manager.get_screen('sync').ids.count.text = '0'
                self.status = False    
            except:
                self.syl.text = 'Error in File'
        except:
            pass

        finally:
            self.sybtn.disabled = False                               
            self.clrbtn.disabled = False                               
            self.btsc.disabled = False                               

                

class MyScreenManager(ScreenManager):
    '''
    def __init__(self, **kwargs):
        super(MyScreenManager, self).__init__(**kwargs)
        self.attribute1 = 'Value 1'
        self.attribute2 = 'Value 2'
        self.currdata = None
        self.mac_add = mac_add
        self.android_id = android_id
        self.imbed = imbed '''
    pass



class TestCamera(App):

    def build(self):
        
        mac_add = 'Not Found'
        wifi = 'Not Found'
        imbed = 'NotFound'
        android_id = 'Not_found' 
        file_path = 'Not_Found'  

        if platform =='android':
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.READ_EXTERNAL_STORAGE,Permission.WRITE_EXTERNAL_STORAGE,Permission.CAMERA,Permission.INTERNET,Permission.ACCESS_WIFI_STATE,Permission.READ_PHONE_STATE])
            
        # getting mac , android , imbed id's
        try : 
            if platform =='android':
                try :          
                    from jnius import autoclass, cast
                    
                    PythonActivity = autoclass('org.kivy.android.PythonActivity')
                    

                    # getting mac_add
                    try:
                        WifiManager = autoclass('android.net.wifi.WifiManager')
                        wifi_manager = cast(WifiManager, PythonActivity.mActivity.getSystemService(PythonActivity.WIFI_SERVICE))
                        wifi_info = wifi_manager.getConnectionInfo()
                        mac_add = wifi_info.getMacAddress()
                        mac_add = str(mac_add)

                    except:
                        mac_add = 'Not found'
                    
                    
                    # getting imbed
                    try:

                        Context = autoclass('android.content.Context')
                        telephonyManager = cast('android.telephony.TelephonyManager', PythonActivity.mActivity.getSystemService(Context.TELEPHONY_SERVICE))
                        imbed = telephonyManager.getDeviceId()
                    except:
                        imbed = 'NotFound'

                    # getting android id
                    try : 
                        SettingsSecure = autoclass('android.provider.Settings.Secure')
                        content_resolver = PythonActivity.mActivity.getContentResolver()
                        android_id = SettingsSecure.getString(content_resolver, SettingsSecure.ANDROID_ID)
                        android_id = str(android_id)
                    except:
                        android_id = 'Not_found'

                except:
                    pass

                # getting wifi_mac                    
                try:
                    from jnius import autoclass, cast
                
                    PythonActivity = autoclass('org.kivy.android.PythonActivity')

                    # Access the Android API classes using Pyjnius
                    WifiManager = autoclass('android.net.wifi.WifiManager')
                    Context = autoclass('android.content.Context')

                    # Get the Wi-Fi service
                    wifi_manager = PythonActivity.mActivity.getSystemService(Context.WIFI_SERVICE)

                    # Check if Wi-Fi is enabled
                    if wifi_manager.isWifiEnabled():
                        # Get the MAC address
                        wifi = wifi_manager.getConnectionInfo().getMacAddress()
                        
                    else:
                        wifi =  "Wi-Fi is disabled"
                except :
                        wifi = 'Not found'



                # getting file_path    
                try:
                    ''' 
                    folder_name = 'qrscan'
                    file_name = 'demo.json'

                    # Get the app-specific directory
                    app_dir = os.path.abspath(os.sep)
                    
                    # Create the folder if it doesn't exist
                    folder_path = os.path.join(app_dir, folder_name)
                    os.makedirs(folder_path, exist_ok=True)
                    
                    # Create the file if it doesn't exist
                    file_path = os.path.join(folder_path, file_name)
                        
                    # if not os.path.exists(file_path):
                    #     with open(file_path, 'w') as file:
                    #         file.write('') '''
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
                    
                    # Create the file if it doesn't exist
                    file_path = join(directory, file_name)

                    file = File(file_path)
                    if not file.exists():
                        file.createNewFile()                            

                except:
                    file_path = ' Not Found'
            
            else :
                #getting mac_add
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
        
        #obj = CameraClick()
        #obj.currdata = None
        screen_manager.currdata = None
        screen_manager.mac_add = str(mac_add)
        screen_manager.android_id = str(android_id)
        screen_manager.imbed = str(imbed)
        screen_manager.wifi = str(wifi)
        screen_manager.code = None
        screen_manager.file_path = file_path
        #screen_manager.sycount = None


        return screen_manager

if __name__ == '__main__':

    TestCamera().run()