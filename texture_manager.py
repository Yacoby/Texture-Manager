# Copyright (c) 2007, Jacob Essex
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY JACOB ESSEX ``AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL JACOB ESSEX BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


#this was written as C/C++ (as you can see from the #define), and I am not sure I
#did some of the things "right"
#if anyone can recomened a good IDE, please say.

import re
import pickle
import struct
import os
import wx
import shutil
import sys
import stat
import sys
import hashlib

###########################################
#           DEFINES
###########################################

PATH_FROM_WORKING_DIR = os.path.basename(sys.path[0])

#added to the path to the game
BASE_DIR    = sys.path[0]
GAME_DIR    = ""
DATA_FILES  = os.path.join(GAME_DIR, "Data Files")

TM_DATA_DIR = os.path.join(PATH_FROM_WORKING_DIR, "TM_Data")
MD5_FILE    = os.path.join(PATH_FROM_WORKING_DIR, "regex.md5")


#DO NOT PUT THIS AS THE ROOT OF THE DRIVE. IT WILL WIPE ALL DATA
INSTALL_DIR = os.path.join(PATH_FROM_WORKING_DIR, "Install")

HOLDING_DIR = os.path.join(TM_DATA_DIR,"Mods")
REGEX_FILE  = os.path.join(TM_DATA_DIR, "Data", "Regex.ini")
DATA_FILE   = os.path.join(TM_DATA_DIR, "Data", "Data.dat")

baseHead, baseTail = os.path.split(BASE_DIR)

WORKING_DIR = baseHead

###########################################

#gets a list of all files
def getFileList(strTop = sys.path[0], bTopDown = False):
    rList = []
    for root, dirs, files in os.walk(strTop, bTopDown):
        root = root.replace(strTop, "", 1)
        root = root.lstrip("\\/")
        for name in files:
            rList.append((os.path.join(root, name)))
    return rList



###########################################
#           FILE CLASS
###########################################

#Contains details about a file.
class File:
    #mName
    #mArcType[]

    
    def __init__(self):
        self.mArcType = []
        #print "New ARC REC"

    # strPath = Path to the file
    # aStrArch = array of string arc types
        

    #below here should be obvious what all does.

    #-----------------------------------------------------------------------
    def addArcType(self, strName):
        self.mArcType.append(strName)

    #-----------------------------------------------------------------------        
    def removeArcType(self, strName):
        self.mArcType.remove(strName)


###########################################
#           MOD CLASS
###########################################
class Mod:

    mName = ""

    #strName = name of the mod
    def __init__(self, strName):
        self.mFile = {}
        self.mName = strName

    #-----------------------------------------------------------------------
    def addFile(self, strName):
        self.mFile[strName] = File()

        #get arch matches
        alist = data.getRegexMatch(strName)
        self.mFile[strName] = alist

        for a in alist:
            data.addArcModData(self.mName, a)
        
    #-----------------------------------------------------------------------
    def addFileArcType(self, strName, arc):
        self.mFile[strName] = File()
        for a in arc:
            self.mFile[strName].addArcType(a)

    #-----------------------------------------------------------------------
    def setName(self, strName):
        self.mName = strName

    #-----------------------------------------------------------------------
    def getName(self):
        return self.mName

###########################################
#           ARC CLASS
###########################################

class Arc:

    mName = ""

    #-----------------------------------------------------------------------
    def __init__(self):
        self.mRegex = []
        self.mModOrder = []
        self.mModOrderDisabled = []

    #-----------------------------------------------------------------------
    def addRegex(self, strRegex):
        self.mRegex.append(re.compile(strRegex, re.IGNORECASE))

    #-----------------------------------------------------------------------
    def getName(self):
        return self.mName

    #-----------------------------------------------------------------------
    def setName(self, strName):
        self.mName = strName

    #-----------------------------------------------------------------------
    #checks if strFile matchtes any of the regex expressions
    #strFile = file
    def isFileMatch(self, strFile):
        for r in self.mRegex:
            if r.match(strFile):
                return True
        return False



    #-----------------------------------------------------------------------
    def addMod(self, strModName):
        if self.mModOrder.count(strModName) == 0:
            self.mModOrder.append(strModName)

    #-----------------------------------------------------------------------
    def removeMod(self, modName):
        if self.mModOrder.count(modName) > 0:
           self.mModOrder.remove(strModName)

    #-----------------------------------------------------------------------
    def addDisabledMod(self, modName):
          if self.mModOrderDisabled.count(modName) == 0:
            self.mModOrderDisabled.append(modName)

    #-----------------------------------------------------------------------
    def removeDisabledMod(self, modName):
        if self.mModOrderDisabled.count(modName) > 0:
            self.mModOrderDisabled.remove(modName)

    #-----------------------------------------------------------------------
    def enableMod(self, modName):
        if self.mModOrderDisabled.count(modName) != 0:
            self.mModOrderDisabled.remove(modName)
            self.mModOrder.append(modName)

    #-----------------------------------------------------------------------
    def disableMod(self, modName):
        if self.mModOrder.count(modName) != 0:
            self.mModOrder.remove(modName)
            self.mModOrderDisabled.append(modName)

    #-----------------------------------------------------------------------
    def removeAllMods(self):
        self.mModOrder = []
        self.mModOrderDisabled = []

    #-----------------------------------------------------------------------
    def moveModUp(self, strName):
        modIndex = self.mModOrder.index(strName)
        
        if modIndex == 0: #at the top of the list already
            return
        
        del self.mModOrder[modIndex]
        self.mModOrder.insert(modIndex - 1, strName)
        
    #-----------------------------------------------------------------------
    def moveModDown(self, strName):
        modIndex = self.mModOrder.index(strName)
        
        if modIndex == len(self.mModOrder) - 1: #at the bottom of the list already
            return
        
        del self.mModOrder[modIndex]
        self.mModOrder.insert(modIndex + 1, strName)


###########################################
#           DATA CLASS
###########################################
class Data:

    mMod = {}
    mArc = {}

    #__shared_state = {}
    #def __init__(self):
     #   self.__dict__ = self.__shared_state

    #-----------------------------------------------------------------------
    def addArcModData(self, strModName, strArc):
        if self.mArc.has_key(strArc) == True:
            self.mArc[strArc].addMod(strModName)


    #-----------------------------------------------------------------------
    def getRegexMatch(self, strFile):
        alist = []
        for a in self.mArc:
            if self.mArc[a].isFileMatch(strFile):
                alist.append(a)
        return alist

    #-----------------------------------------------------------------------
    def updateArcData(self):

        #clear all arc data
        for k in self.mArc:
            self.mArc[k].removeAllMods()

        #go through every mod, every file, and get regex matches
        for m in self.mMod:
            for f in self.mMod[m].mFile:

                #reset arch data for the file
                try:
                    self.mMod[m].mFile[f].mArcType = []
                except:
                    pass            

                arcList = self.getRegexMatch(f)
                self.mMod[m].mFile[f] = arcList

                for a in arcList:
                    data.addArcModData(m, a)
                
                

    #-----------------------------------------------------------------------
    #arc regex data is in a seperate, plain text file. This is to allow easy editing
    #regex file is layed out like so:
    #[ArcName]
    #Regex1
    #Regex2
    #etc
    def loadRegex(self, fileName):
        if os.path.exists(fileName) == False:
            return

        print "\nLoading Regex..."
        
        ifs = open(fileName, 'r')
        lines = ifs.readlines()
        
        curArc = None
        for l in lines:
            l = l.strip(" ")
            if l == "" or l.find(";") == 0:
                 continue
            
            match  = re.match('\\[(.*)\\]', l)
            if match != None:
                curArc = match.group(1)
            elif curArc != None:
                if self.mArc.has_key(curArc) != True:
                    self.mArc[curArc] = Arc()
                    self.mArc[curArc].setName(curArc)
                self.mArc[curArc].addRegex(l)
                        

    #-----------------------------------------------------------------------
    #loads all data, including 
    def save(self, fileName):
        #--Write header---#
        # (file ver Major - Minor )
        ofs = file(fileName,"wb")
        pickle.dump(self.mMod, ofs)
        pickle.dump(self.mArc, ofs)
        ofs.close()

    #-----------------------------------------------------------------------
    def load(self, fileName):
        if os.path.exists(fileName) == False:
            return
        ifs = open(fileName, "rb")
        self.mMod = pickle.load(ifs)
        self.mArc = pickle.load(ifs)
        ifs.close()

    #-----------------------------------------------------------------------
    def addMod(self, modName, files):
        print "Adding files to " + modName
        self.mMod[modName] = Mod(modName)
        for f in files:
            print "-- " + f
            self.mMod[modName].addFile(f)
        

    #-----------------------------------------------------------------------
    #copys every mod to the data files directory
    def installAllData(self):
        pass

########################################################

class Directory:

    def __init__(self):
        self.mFile = {}
        
    def add(self, strFile, strMod):
        self.mFile[strFile] = strMod

    def get(self):
        return self.mFile

########################################################
    

data = Data()
    

########################################################
#                MAIN GUI FORM
########################################################

ID_INSTALL=101
ID_UNINSTALL=102
ID_APPLY = 103
ID_MOD_LIST=111

ID_ARC_LIST=121

ID_ARC_UP = 131
ID_ARC_DOWN = 132
ID_ARC_ENABLE = 133
ID_ARC_DISABLE = 134

class MainForm(wx.Dialog):
    def __init__(self):
        wx.Dialog.__init__(self, None, wx.ID_ANY, 'Texture Manager', wx.Point(-1, -1), wx.Size(500, 420))

        #close
        wx.EVT_CLOSE(self, self.OnClose)
        #self.Bind(wx.EVT_CLOSE, self.OnClose)

        #installing
        self.btnInstall = wx.Button(self, ID_INSTALL, "Install", wx.Point(8, 24), wx.Size(75, 23))
        self.txtInstall = wx.TextCtrl(self, -1, "", wx.Point(96, 24), wx.Size(200, 21))

        wx.EVT_BUTTON(self, ID_INSTALL, self.OnInstall)

        #uninstalling
        self.btnUninstall = wx.Button(self, ID_UNINSTALL, "Uninstall", wx.Point(8, 64), wx.Size(75, 23))
        wx.EVT_BUTTON(self, ID_UNINSTALL, self.OnUninstallClick)


        #list of installed mods and files
        self.lstMods = wx.ListBox(self, ID_MOD_LIST, wx.Point(96, 64), wx.Size(200, 112))
        self.lstFiles = wx.ListBox(self, -1, wx.Point(304, 24), wx.Size(168, 152))

        wx.EVT_LISTBOX(self, ID_MOD_LIST, self.OnModList)

        for m in data.mMod:
            self.lstMods.Append(m)

        #list of arcs
        self.lstArcs = wx.ListBox(self, ID_ARC_LIST, wx.Point(8, 192), wx.Size(200, 168))

        wx.EVT_LISTBOX(self, ID_ARC_LIST, self.OnArcList)
        
        for a in data.mArc:
            self.lstArcs.Append(a)

        

        #enabled box
        self.lstArcEnabled = wx.ListBox(self, -1, wx.Point(224, 192), wx.Size(168, 102))

        #disabled box
        self.lstArcDisabled = wx.ListBox(self, -1, wx.Point(224, 304), wx.Size(168, 56))

        wx.Button(self, ID_ARC_UP, "Move Up", wx.Point(400, 192), wx.Size(75, 23))
        wx.EVT_BUTTON(self, ID_ARC_UP, self.OnMoveUpClick)

        
        
        wx.Button(self, ID_ARC_DOWN, "Move Down", wx.Point(400, 224), wx.Size(75, 23))
        wx.EVT_BUTTON(self, ID_ARC_DOWN, self.OnMoveDownClick)
         
        wx.Button(self, ID_ARC_DISABLE, "Disable", wx.Point(400, 272), wx.Size(75, 23))
        wx.EVT_BUTTON(self, ID_ARC_DISABLE, self.OnDisableClick)
        
        wx.Button(self, ID_ARC_ENABLE, "Enable", wx.Point(400, 304), wx.Size(75, 23))
        wx.EVT_BUTTON(self, ID_ARC_ENABLE, self.OnEnableClick)


        #apply changes
        self.btnApply = wx.Button(self, ID_APPLY, "Apply Change", wx.Point(8, 154), wx.Size(75, 23))
        wx.EVT_BUTTON(self, ID_APPLY, self.OnApplyClick)
        


    #-----------------------------------------------------------------------
    def fillExportData(self):
        root = Directory()

        #get the unknow files
        for m in data.mMod:
            for f in data.mMod[m].mFile:
                try:
                    if len(data.mMod[m].mFile[f].mArcType) == 0:
                        root.add(f, m)
                except:
                    root.add(f, m)

        for a in data.mArc: #every arc type
            for m in data.mArc[a].mModOrder: #every mod within that type
                for f in data.mMod[m].mFile: 
                    for t in data.mMod[m].mFile[f].mArcType:
                        if t == a: #for every file related to that type
                            root.add(f, m) #add the file
        return root
        
    #-----------------------------------------------------------------------
    def OnApplyClick(self, e):
        print "\nGening File List..."
        files = self.fillExportData()
        for f in files.get():
            sFromPath = os.path.join(HOLDING_DIR, files.get()[f], f)
            sToPath   = os.path.join(DATA_FILES, f)

            head, tail = os.path.split(sToPath)

            print "\nCreate Dir: " + head + "\n--Move : " + sFromPath + "\n--To: " + sToPath

            if os.path.exists(head) == False:
                os.makedirs(head)
            
            shutil.copy(sFromPath, sToPath)
        
    #-----------------------------------------------------------------------
    def OnUninstallClick(self, e):
        print "\nGening File List..."
        files = self.fillExportData()

        mod = self.lstMods.GetStringSelection()

        print "Removing Files:"
        for f in files.get():
            if files.get()[f] == mod:
                print "-- " + os.path.join(DATA_FILES, f)
                os.remove(os.path.join(DATA_FILES, f))

        #now need to remove all data relating to the mod
        shutil.rmtree(os.path.join(HOLDING_DIR, mod))

        del data.mMod[mod]

        #loop through every arc type, and delete mod
        for a in data.mArc:
            data.mArc[a].removeMod(mod)
            data.mArc[a].removeDisabledMod(mod)
        
        self.lstMods.Delete( self.lstMods.GetSelection() )

    #-----------------------------------------------------------------------
    def OnArcList(self, e):
        if self.lstArcs.GetStringSelection() == "":
            return

        self.lstArcEnabled.Clear()
        self.lstArcDisabled.Clear()


        self.lstFiles.Clear()
        for f in data.mArc[self.lstArcs.GetStringSelection()].mModOrder:
            self.lstArcEnabled.Append(f)

        for f in data.mArc[self.lstArcs.GetStringSelection()].mModOrderDisabled:
            self.lstArcDisabled.Append(f)


    #-----------------------------------------------------------------------
    def OnDisableClick(self, e):
        if self.lstArcEnabled.GetSelection() == wx.NOT_FOUND:
            return

        self.btnUninstall.Disable()
        self.btnApply.Enable()
        
        index = self.lstArcEnabled.GetSelection()
        mod = self.lstArcEnabled.GetString(index)
        
        self.lstArcEnabled.Delete(index)
        self.lstArcDisabled.Append(mod)

        data.mArc[self.lstArcs.GetStringSelection()].disableMod(mod)
        
    #-----------------------------------------------------------------------
    def OnEnableClick(self, e):
        if self.lstArcDisabled.GetSelection() == wx.NOT_FOUND:
            return

        self.btnUninstall.Disable()
        self.btnApply.Enable()
        
        index = self.lstArcDisabled.GetSelection()
        mod = self.lstArcDisabled.GetString(index)
        
        self.lstArcDisabled.Delete(index)
        self.lstArcEnabled.Append(mod)

        data.mArc[self.lstArcs.GetStringSelection()].enableMod(mod)

    #-----------------------------------------------------------------------
    def OnMoveUpClick(self, e):
        if self.lstArcEnabled.GetSelection() == wx.NOT_FOUND:
            return

        self.btnUninstall.Disable()
        self.btnApply.Enable()


        index = self.lstArcEnabled.GetSelection()

        if index == 0:
            return
        
        mod = self.lstArcEnabled.GetString(index)

        self.lstArcEnabled.Delete(index)
        self.lstArcEnabled.Insert(mod, index - 1)
        self.lstArcEnabled.Select(index - 1)

        data.mArc[self.lstArcs.GetStringSelection()].moveModUp(mod)
        
        
    #-----------------------------------------------------------------------
    def OnMoveDownClick(self, e):
        if self.lstArcEnabled.GetSelection() == wx.NOT_FOUND:
            return

        self.btnUninstall.Disable()
        self.btnApply.Enable()

        index = self.lstArcEnabled.GetSelection()

        if index == self.lstArcEnabled.GetCount() - 1:
            return
        
        mod = self.lstArcEnabled.GetString(index)

        self.lstArcEnabled.Delete(index)
        self.lstArcEnabled.Insert(mod, index + 1)
        self.lstArcEnabled.Select(index + 1)

        data.mArc[self.lstArcs.GetStringSelection()].moveModDown(mod)

    #-----------------------------------------------------------------------
    def OnClose(self, e = 0):
        print "Saving Data..."
        
        #data = Data()
        data.save(DATA_FILE)

        print "Exiting..."        
        self.Destroy()

    #-----------------------------------------------------------------------
    def OnModList(self, e):
        #data = Data()

        if self.lstMods.GetStringSelection() == "":
            return

        print "Selected: " + self.lstMods.GetStringSelection()

        self.lstFiles.Clear()
        for f in data.mMod[self.lstMods.GetStringSelection()].mFile:
            self.lstFiles.Append(f)

    #-----------------------------------------------------------------------
    def OnInstall(self, e):
        strVal = self.txtInstall.GetValue()
        print "Mod Name: " + strVal
        if len(strVal) == 0:
            d= wx.MessageDialog( self, "You must enter a unique name for the mod", "Error", wx.OK)
            d.ShowModal()
            d.Destroy() 
            return

        self.btnUninstall.Disable()
        self.btnApply.Enable()

        #record mod data
        print "Getting file list..."
        files = getFileList(INSTALL_DIR)

        #data = Data()
        data.addMod(strVal, files)


        #copy
        print "Copying files..."
        shutil.copytree(INSTALL_DIR, os.path.join(HOLDING_DIR, strVal))

        #del old
        print "Remvoing..."
        for root, dirs, files in os.walk(INSTALL_DIR, False):
            for name in files:
                os.remove(os.path.join(root, name))
                print "--- " + os.path.join(root, name)
            for name in dirs:
                os.rmdir(os.path.join(root, name))
                print "--- " + os.path.join(root, name)

        print "Adding to list"
        self.lstMods.Append(strVal)
    #-----------------------------------------------------------------------


                
        
########################################################
#                       Startup
########################################################


print "Setting Working Dir to " + WORKING_DIR
os.chdir(WORKING_DIR)

#get the md5 of the regex.ini
print "Checking Regex..."
m = hashlib.md5()
fs = open(REGEX_FILE, 'r')
lines = fs.readlines()
for l in lines:
    m.update(l)
newMd5 = m.hexdigest()

oldMd5 = newMd5

print "Comparing..."
if os.path.exists(MD5_FILE) == True:
    fs = open(MD5_FILE, 'r')
    oldMd5 = fs.readline()
else:
    fs = open(MD5_FILE, 'w')
    fs.write(newMd5)

regexFileUpdated = False
if oldMd5 != newMd5:
    fs = open(MD5_FILE, 'w')
    fs.write(newMd5)
    regexFileUpdated = True
    print "Regex file has changed"
else:
    print "Regex fine"




print "Loading Data..."
#data = Data()
data.load(DATA_FILE)
data.loadRegex(REGEX_FILE)
print "Starting App..."



app = wx.PySimpleApp()

#check to see if regex update is wanted
if regexFileUpdated:
    dlg = wx.MessageDialog(None, 'The Regex file has been changed. Do you want to update your the list of mods assoiated with each architecture type to reflect this change \n(Note: Mod Load Order will be lost)', 'REGEX Change', wx.YES | wx.NO | wx.ICON_INFORMATION)
    result = dlg.ShowModal()
    if result == wx.ID_YES:
        data.updateArcData() #this is broken IIRC



#start app
frame = MainForm()
frame.Show(True)
app.MainLoop()

