from resources.lib.xbmcguie.xbmcContainer import *
from resources.lib.xbmcguie.xbmcControl import *
from resources.lib.xbmcguie.tag import Tag
from resources.lib.xbmcguie.category import Category,Setting

#from lib.NetworkCustomControlSetting import NetworkSettings

from resources.lib.xbianconfig import xbianConfig
from resources.lib.utils import *

import xbmcgui
import os

dialog=xbmcgui.Dialog()

class NewtorkLabel(Setting) :
    CONTROL = CategoryLabelControl(Tag('label','Network'))
    
class NetworkControl(MultiSettingControl):
    XBMCDEFAULTCONTAINER = False
    DHCP = 'Dhcp'
    STATIC = 'Static'
    
    def onInit(self) :
        self.interface = SpinControlex(Tag('label','Interface'))
        self.addControl(self.interface)
        self.interfacelist = xbianConfig('network','list')
        self.interfaceValue = {}

        for interface in self.interfacelist :
             self.interfaceValue[interface] = {}
             self.interfaceValue[interface]['content'] = Content(Tag('label',interface),defaultSKin=False)
             self.interface.addContent(self.interfaceValue[interface]['content'])
             
             #create the interface group
             self.interfaceValue[interface]['group'] = MultiSettingControl(Tag('visible','Container(%d).HasFocus(%d)'%(self.interface.getWrapListId(),self.interfaceValue[interface]['content'].getId())))
             self.addControl(self.interfaceValue[interface]['group'])
             
             #add status control
             self.interfaceValue[interface]['status'] = ButtonControl(Tag('label',' -Status'))
             self.interfaceValue[interface]['group'].addControl(self.interfaceValue[interface]['status'])
             
             #add interface mode Control (static/dhcp)
             self.interfaceValue[interface]['mode'] = SpinControlex(Tag('label',' -Mode'))
             dhcp = Content(Tag('label',self.DHCP),defaultSKin=False)
             static = Content(Tag('label',self.STATIC),defaultSKin=False)
             self.interfaceValue[interface]['mode'].addContent(dhcp)
             self.interfaceValue[interface]['mode'].addContent(static)
             self.interfaceValue[interface]['group'].addControl(self.interfaceValue[interface]['mode'])
             
             #add Static Group
             self.interfaceValue[interface]['staticgroup'] = MultiSettingControl(Tag('visible','Container(%d).HasFocus(%d)'%(self.interfaceValue[interface]['mode'].getWrapListId(),static.getId())))
             self.interfaceValue[interface]['ipadress'] = ButtonControl(Tag('label','  -Adress'))
             self.interfaceValue[interface]['subnet'] = ButtonControl(Tag('label','  -Subnet'))
             self.interfaceValue[interface]['gateway'] = ButtonControl(Tag('label','  -Gateway'))
             self.interfaceValue[interface]['dns1'] = ButtonControl(Tag('label','  -Primary Dns'))
             self.interfaceValue[interface]['dns2'] = ButtonControl(Tag('label','  -Secondary Dns'))
             self.interfaceValue[interface]['staticgroup'].addControl(self.interfaceValue[interface]['ipadress'])
             self.interfaceValue[interface]['staticgroup'].addControl(self.interfaceValue[interface]['subnet'])
             self.interfaceValue[interface]['staticgroup'].addControl(self.interfaceValue[interface]['gateway'])
             self.interfaceValue[interface]['staticgroup'].addControl(self.interfaceValue[interface]['dns1'])
             self.interfaceValue[interface]['staticgroup'].addControl(self.interfaceValue[interface]['dns2'])
             self.interfaceValue[interface]['group'].addControl(self.interfaceValue[interface]['staticgroup'])
             
             #check if Wifi
             self.interfaceValue[interface]['wifi'] = False
             if os.path.exists("/sys/class/net/%s/wireless"%interface) :
                 self.interfaceValue[interface]['wifi'] = True
                 self.interfaceValue[interface]['ssid'] = ButtonControl(Tag('label',' -Ssid'))
                
    def setValue(self,values):
        default = values[0]
        self.interface.setValue(default)
        networkValue = values[1]
        for key in networkValue :
            value = networkValue[key]
            if value[0] == 'static' :
                self.interfaceValue[key]['mode'].setValue(self.STATIC)
            else :
                self.interfaceValue[key]['mode'].setValue(self.DHCP)
         
            self.interfaceValue[key]['status'].setValue(value[1])    
            self.interfaceValue[key]['ipadress'].setValue(value[2])
            self.interfaceValue[key]['ipadress'].onClick = lambda ipadress: self.interfaceValue[key]['ipadress'].setValue(getIp('Ip adress',value[2]))
            self.interfaceValue[key]['subnet'].setValue(value[3])
            self.interfaceValue[key]['subnet'].onClick = lambda subnet: self.interfaceValue[key]['subnet'].setValue(getIp('Subnet',value[3]))
            self.interfaceValue[key]['gateway'].setValue(value[4])
            self.interfaceValue[key]['gateway'].onClick = lambda gateway: self.interfaceValue[key]['gateway'].setValue(getIp('Gateway',value[4]))
            self.interfaceValue[key]['dns1'].setValue(value[5])
            self.interfaceValue[key]['dns1'].onClick = lambda dns1: self.interfaceValue[key]['dns1'].setValue(getIp('Primary Dns',value[5]))
            self.interfaceValue[key]['dns2'].setValue(value[6])
            self.interfaceValue[key]['dns2'].onClick = lambda dns2: self.interfaceValue[key]['dns2'].setValue(getIp('Secondary Dns',value[6]))
            
            if self.interfaceValue[key]['wifi'] :
                self.interfaceValue[key]['ssid'].setValue('%s (%s)'%(value[8],value[7]))
                self.interfaceValue[key]['ssid'].onClick =  lambda ssid : self.interfaceValue[key]['ssid'].setValue(wifiConnect(key,value[8],value[7]))
   
    def getValue(self) :
       default = self.interface.getValue()
       networkValue = {}
       for interface in self.interfacelist :
           networkValue[interface] = self.interfaceValue[interface]['group'].getValue()
           #swap status and mode to be compliant with xbian_config
           tmp = networkValue[interface][0]
           networkValue[interface][0] = networkValue[interface][1].lower()
           networkValue[interface][1] = tmp
           
       return [default,networkValue]
        
class NetworkSetting(Setting) :
    CONTROL = NetworkControl()
    DIALOGHEADER = "NETWORK SETTINGS"
    ERRORTEXT = "Error on updating"
    OKTEXT = "Update ok"
    SAVEMODE = Setting.ONUNFOCUS
    
#    def setControlValue(self,value): 
#            self.getControl().setValue(val)
    
    def getUserValue(self):
        return self.getControl().getValue()
    
    def getXbianValue(self):
        default = False
        self.lanConfig={}
        for interface in self.getControl().interfacelist :
            interface_config = xbianConfig('network','status',interface)
            if interface_config[2] == 'UP' or not default :
                default = interface
            self.lanConfig[interface] = []
            for config in interface_config :
                try :
                    self.lanConfig[interface].append(config.split(' ')[1])
                except :
                    self.lanConfig[interface].append(None)    
        return [default,self.lanConfig]
    
    def setXbianValue(self,values):
        #interface,status,mode,ipadress,subnet,gateway,dns1,dns2,ssid=None
        interface = values[0]
        value = values[1][interface]
        if value[0].lower() == NetworkControl.DHCP.lower() :
            mode = 'dhcp'
            cmd = [mode,interface]
        else :
            mode = 'static'
            if value[6] == '' :
                value[6] = value[5]
            cmd = [mode,interface,value[2],value[3],value[4],value[5],value[6]]
        rc = xbianConfig('network',*cmd)
        ok = True
        if not rc :
            ok = False
            self.ERRORTEXT = "No return Code From Xbian"
        elif rc[0] != '1' : 
            ok = False
            self.ERRORTEXT = rc[1]
        return ok           
        
        
class LicenceLabel(Setting) :
    CONTROL = CategoryLabelControl(Tag('label','Licenses'))

class mpeg2License(Setting) :
    CONTROL = ButtonControl(Tag('label','MPG2'))
    DIALOGHEADER = "MPEG2 License"
    ERRORTEXT = "Error updating"
    OKTEXT = "Update ok"
    BADUSERENTRYTEXT = "must be hex and looks like 0x00000000"
    
    def onInit(self) :
        self.xbiankey = 'licensempg2'
        
    def getUserValue(self):
        return getText(self.DIALOGHEADER,self.getControlValue())
        
    def checkUserValue(self,value):
        try :
            hexvalue = int(value,16)
            keyok = len(value) == 10 and value[:2] == '0x'
        except :
            keyok = False   
        return keyok
    
    def getXbianValue(self):
        licenseValue =xbianConfig(self.xbiankey,'select')
        if licenseValue and licenseValue[0][:2] == '0x' :
            self.XbianLicenseCmd = 'update'
            return licenseValue[0]
        else :
            if len(licenseValue) == 0 or licenseValue[0] == "" :
                self.XbianLicenseCmd = 'insert'
            else :
                self.XbianLicenseCmd = 'update'
            return '0x'                  
    
        
    def setXbianValue(self,value):
        rc = xbianConfig(self.xbiankey,self.XbianLicenseCmd,value)
        ok = True
        if not rc: 
            ok = False
        elif rc[0] != '1' :
            ok = False
        return ok       
        
    
class vc1License(mpeg2License) :
    CONTROL = ButtonControl(Tag('label','VC1'))
    DIALOGHEADER = "VC1 License"
    
    def onInit(self) :
        self.xbiankey = 'licensevc1'
    
class connectivityLabel(Setting) :
    CONTROL = CategoryLabelControl(Tag('label','Connectivity'))

class videooutputControl(MultiSettingControl):
    XBMCDEFAULTCONTAINER = False
    
    def onInit(self) :
        self.videooutputlist = xbianConfig('videoflags','list')
        self.videooutputcontrol = {}
        for videooutput in self.videooutputlist :
            guiname = videooutput.replace('_',' ').capitalize()
            self.videooutputcontrol[videooutput] = RadioButtonControl(Tag('label',guiname))
            self.videooutputcontrol[videooutput].onClick = lambda forwardclick : self.onClick(self)
            self.addControl(self.videooutputcontrol[videooutput])
        
    def setValue(self,values) :
        for key in values :
            if values[key] == '1' :
                boolvalue = True
            else :
                boolvalue = False
            self.videooutputcontrol[key].setValue(boolvalue)
            
    def getValue(self) :
        rc = {}
        for videooutput in self.videooutputlist :
            rc[videooutput] = str(self.videooutputcontrol[videooutput].getValue())
        return rc
            
            
            

class videooutput(Setting) :
    CONTROL = videooutputControl()
    DIALOGHEADER = "Video Output "
    ERRORTEXT = "Error on updating"
    OKTEXT = "Update ok"
                    
    def onInit(self) :
        self.listvalue = xbianConfig('videoflags','list')
        self.value = {}
        
    def getUserValue(self):
        return self.getControlValue()
    
    def getXbianValue(self):
        for value in self.listvalue :
            if not self.value.has_key(value) :
                self.value[value] = xbianConfig('videoflags','select',value)[0]
        return self.value
        
    def setXbianValue(self,value):
        #set xbian config here
        print value
        for key in value :
            if value[key] != self.xbianValue[key] :
                 rc = xbianConfig('videoflags','update',key,value[key])
                 self.DIALOGHEADER = key.replace('_',' ').title()
                 break
        if rc and rc[0] == '1' :
            return True
        else :
            return False

class SytemLabel(Setting) :
    CONTROL = CategoryLabelControl(Tag('label','System'),Tag('visible','skin.hasSetting(advancedmode)'))
    
    def onInit(self):
        #check if advanced mode is set
        #must check here and not in preference since value are read one by one when plugin start.
        #and this setting is read before preference - advanced mode
        key = 'advancedmode'
        rc = self.getSetting(key)
        if rc == '1' :
            xbmc.executebuiltin('Skin.SetBool(%s)'%key)
        else :
            xbmc.executebuiltin('Skin.Reset((%s)'%key)
    
class hostname(Setting) :
    CONTROL = ButtonControl(Tag('label','Hostname'),Tag('visible','skin.hasSetting(advancedmode)'))
    DIALOGHEADER = "Host Name"
    ERRORTEXT = "Error updating"
    OKTEXT = "Update ok"
    BADUSERENTRYTEXT = "Format is not Correct,bad carachter inside"
        
    def getUserValue(self):
        return getText(self.DIALOGHEADER,self.getControlValue())
        
    def checkUserValue(self,value):
        return value.isalnum()
    
    def getXbianValue(self):
        licenseValue =xbianConfig('hostname','select')
        if licenseValue :
            return licenseValue[0]
        else :
            return ''                
        
    def setXbianValue(self,value):
        rc = xbianConfig('hostname','update',value)
        ok = True
        if not rc: 
            ok = False
        elif rc[0] != '1' :
            ok = False
        return ok       

class kernel(Setting) :
    CONTROL = SpinControlex(Tag('label','Kernel'),Tag('visible','skin.hasSetting(advancedmode)'))
    DIALOGHEADER = "Kernel Version"
    ERRORTEXT = "Error updating"
    OKTEXT = "Update ok"
    SAVEMODE = Setting.ONUNFOCUS
    
    def onInit(self):
        kernellist =xbianConfig('kernel','list')
        for kernel in kernellist :
            content = Content(Tag('label',kernel),defaultSKin=False)
            self.control.addContent(content)

    def getUserValue(self):
        return self.control.getValue()
        
    def getXbianValue(self):
        kernelVersion =xbianConfig('kernel','select')
        if kernelVersion :
            return kernelVersion[0]
        else :
            return ''                
        
    def setXbianValue(self,value):
        rc = xbianConfig('kernel','update',value)
        ok = True
        if not rc: 
            ok = False
        elif rc[0] != '1' :
            if rc[0] == '-1' :
                self.ERRORTEXT = 'Insufficient number of arguments'
            elif rc[0] == '-2' :
                self.ERRORTEXT = 'Already running this kernel'
            elif rc[0] == '-3' :
                self.ERRORTEXT = "Kernel version doesn't exist"
            ok = False
        return ok

class OverclockControl(MultiSettingControl):
    XBMCDEFAULTCONTAINER = False
    
    def onInit(self) :
        self.overclockMode = SpinControlex(Tag('label','Overclocking'))
        self.addControl(self.overclockMode)
        self.overclockinglist = xbianConfig('overclocking','list')

        for mode in self.overclockinglist :
             content = Content(Tag('label',mode),defaultSKin=False)
             self.overclockMode.addContent(content)
             if mode == 'Custom' :
                 self.customOverclock = MultiSettingControl(Tag('visible','Container(%d).HasFocus(%d)'%(self.overclockMode.getWrapListId(),content.getId())))
                 self.Arm = ButtonControl(Tag('label',' -Arm'))
                 self.Core = ButtonControl(Tag('label',' -Core'))
                 self.Sdram = ButtonControl(Tag('label',' -SDram'))
                 self.Overvoltage = ButtonControl(Tag('label',' -Overvoltage'))
                 self.customOverclock.addControl(self.Arm)
                 self.customOverclock.addControl(self.Core)
                 self.customOverclock.addControl(self.Sdram)
                 self.customOverclock.addControl(self.Overvoltage)
                 self.addControl(self.customOverclock)
    
    def setValue(self,value):
        if value :            
            #trick to get list in lower case
            for val in self.overclockinglist :
                if value[0] == val.lower() :
                    break
            self.overclockMode.setValue(val)
            self.Arm.setValue(value[1])
            self.Arm.onClick = lambda arm: self.Arm.setValue(getNumeric('Arm Overclocking',value[1],400,1200))
            self.Core.setValue(value[2])    
            self.Core.onClick = lambda core: self.Core.setValue(getNumeric('Arm Overclocking',value[2],100,600))
            self.Sdram.setValue(value[3])
            self.Sdram.onClick = lambda sdram: self.Sdram.setValue(getNumeric('Arm Overclocking',value[3],100,600))
            self.Overvoltage.setValue(value[4])
            self.Overvoltage.onClick = lambda overvolt: self.Overvoltage.setValue(getNumeric('Arm Overclocking',value[4],0,12))

class overclocking(Setting) :
    CONTROL = OverclockControl(Tag('visible','skin.hasSetting(advancedmode)'))
    DIALOGHEADER = "Overclocking"
    ERRORTEXT = "Error updating"
    OKTEXT = "Update ok"
    SAVEMODE = Setting.ONUNFOCUS
            
    def getUserValue(self):
        values =  self.control.getValue()
        if values :
            values[0] = values[0].lower()
        return values
        
    def getXbianValue(self):
        overclock =xbianConfig('overclocking','select')
        value = xbianConfig('overclocking','values')       
        if overclock and value:
            overclock.extend(value[0].split(' '))          
            return overclock
        else :
            return []                
        
    def setXbianValue(self,value):
        if value[0] != 'custom' :
            val = [value[0]]
        else :
            val = value
        
        rc = xbianConfig('overclocking','update',*val)
        ok = True
        if not rc: 
            ok = False
        elif rc[0] != '1' :
            if rc[0] == '-1' :
                self.ERRORTEXT = "preset doesn't exist"
            elif rc[0] == '-2' :
                self.ERRORTEXT = 'invalid number of arguments'
            elif rc[0] == '-3' :
                self.ERRORTEXT = "non-numeric arguments"
            ok = False
        return ok


class timezone(Setting) :
    CONTROL = ButtonControl(Tag('label','Timezone'),Tag('visible','skin.hasSetting(advancedmode)'))
    DIALOGHEADER = "TimeZone"
    ERRORTEXT = "Error updating"
    OKTEXT = "Update ok"
    
    def setControlValue(self,value) :
        self.control.setValue('%s / %s'%(value[0].title(),value[1].title()))
            
    def getUserValue(self):
        continentList = xbianConfig('timezone','list')
        continentgui = []
        for continent in continentList :
            continentgui.append(continent.title())
        rcr = dialog.select('Region',continentgui)
        if rcr != -1 :
            countrylist = xbianConfig('timezone','list',continentList[rcr])
            countrygui = []
            for country in countrylist :
                countrygui.append(country.title())
            rcc = dialog.select('Country',countrygui)
            if rcc != -1 :
               return [continentList[rcr],countrylist[rcc]]
        return self.xbianValue
        
    def getXbianValue(self):
        timezone =xbianConfig('timezone','select')
        print timezone
        if timezone and timezone[0] != '-1':
            return(timezone[0].split(' '))          
        else :
            return ['Not Set','Not Set']                
        
    def setXbianValue(self,value):
        rc = xbianConfig('timezone','update',*value)
        ok = True
        if not rc or not rc[0]: 
            ok = False
        return ok

class AccountLabel(Setting) :
    CONTROL = CategoryLabelControl(Tag('label','Account'),Tag('visible','skin.hasSetting(advancedmode)'))
    
    def onInit(self):
        #check if advanced mode is set
        #must check here and not in preference since value are read one by one when plugin start.
        #and this setting is read before preference - advanced mode
        key = 'advancedmode'
        rc = self.getSetting(key)
        if rc == '1' :
            xbmc.executebuiltin('Skin.SetBool(%s)'%key)
        else :
            xbmc.executebuiltin('Skin.Reset((%s)'%key)
    
class rootpwd(Setting) :
    CONTROL = ButtonControl(Tag('label','Root Password'),Tag('visible','skin.hasSetting(advancedmode)'))
    DIALOGHEADER = "Root Password"
    ERRORTEXT = "Error updating"
    OKTEXT = "Update ok"
    BADUSERENTRYTEXT = "Password does not match"
        
    def onInit(self):
        self.forceUpdate = True
        self.password = None
        self.key = 'rootpass'
        
    def checkUserValue(self,value):
        return self.password == self.confirmpwd
    def getUserValue(self):
        self.password = getText(self.DIALOGHEADER,hidden=True)
        self.confirmpwd = getText('Confirm ' + self.DIALOGHEADER,hidden=True)
        return '*****'
        
    def getXbianValue(self):
        return '*****'                
        
    def setXbianValue(self,value):
        rc = xbianConfig(self.key,'update',self.password)
        ok = True
        if not rc: 
            ok = False
        elif rc[0] != '1' :
            ok = False
        return ok       

class xbianpwd(rootpwd) :
    CONTROL = ButtonControl(Tag('label','XBian password'),Tag('visible','skin.hasSetting(advancedmode)'))
    DIALOGHEADER = "Xbian Password"
    
    def onInit(self):
        self.forceUpdate = True
        self.password = None
        self.key = 'xbianpass'
    
class sshroot(Setting) :
    CONTROL = RadioButtonControl(Tag('label','Allow SSH root login'),Tag('visible','skin.hasSetting(advancedmode)'))
    DIALOGHEADER = "SSH root"
    ERRORTEXT = "Error on updating"
    OKTEXT = "Update ok"
    
                    
    def getUserValue(self):
        return str(self.getControlValue())
    
    def setControlValue(self,value) :
        if value == '1' :
            value = True
        else :
            value = False
        self.control.setValue(value)
    
    def getXbianValue(self):
        rc = xbianConfig('sshroot','status')
        return rc[0]
        
    def setXbianValue(self,value):
        if value == '1':
            cmd = 'enable'
        else :
            cmd = 'disable'
        rc = xbianConfig('sshroot',cmd)
        ok = True
        if not rc: 
            ok = False
        elif rc[0] != '1' :
            ok = False
        return ok       

#CATEGORY CLASS
class system(Category) :
    TITLE = 'System'
    SETTINGS = [NewtorkLabel,NetworkSetting,LicenceLabel,mpeg2License,vc1License,connectivityLabel,videooutput,SytemLabel,hostname,timezone,kernel,overclocking,AccountLabel,rootpwd,xbianpwd,sshroot]
