#coding:utf-8
#-------------------------------------------------------------------------------
# Name:        PubIng2012_MainFrame.py
# Purpose:
#
# Author:      wid
#
# Created:     26-11-2012
# Copyright:   (c) wid 2012
# Licence:     GNU GPL
#-------------------------------------------------------------------------------

import wx
import time
import random
import urllib
import urllib2
import win32api
import win32gui
import cookielib
import threading
import PubIng2012_AboutDlg
import PubIng2012_LoginCnblogsDlg

def en(x):
    return x.encode('utf-8')

def cn(x):
    return x.decode('utf-8')

class ThreadWork( threading.Thread ):
    def __init__( self, parent,  username, password, intervalTime ):
        threading.Thread.__init__( self )
        self.parent = parent
        self.username = username
        self.password = password
        self.intervalTime = intervalTime

        self.ThreadIsRun = True           #线程控制

    def run(self):
        self.Work()

    def stop(self):
        self.ThreadIsRun = False

    def Work( self ):
        status = self.LogoinCnblogs( self.username, self.password )
        if status != 1:
            wx.CallAfter( self.parent.ShowErrors, status )
            return
        self.WriteLog( '执行刷星命令' )

        try:
            with open( 'src/PubIng2012_IngContent.txt', 'r' ) as f:
                txt = f.readlines()
        except:
            wx.CallAfter( self.parent.ShowErrors, '请先设置发布内容!' )
            return

        while self.ThreadIsRun:
            PubInfo = []
            PubInfo.append(str( time.strftime("%Y-%m-%d %X", time.localtime()) ))
            pubContent = random.choice(txt)
            pubContent = pubContent.rstrip()
            pubContent = unicode(pubContent, "UTF-8")   #
            PubInfo.append( pubContent )
            status = self.PubishIng( pubContent )
            if status != 1:
                self.WriteLog( '该闪存发布失败: %s'%en(pubContent) )
                PubInfo.append( u'发布失败' )
            else:
                self.WriteLog( '成功发布闪存: %s'%en(pubContent) )
                PubInfo.append( u'发布成功' )
            status = self.CheckIsStarIng(en(pubContent))
            if status == 1:
                PubInfo.append( u'这是幸运闪' )
                self.WriteLog( '这是幸运闪' )
            else:
                PubInfo.append( u'否' )
            wx.CallAfter( self.parent.ReDrawListCtrl, PubInfo )
            self.WriteLog('----------\r\n')
            for i in range( self.intervalTime, 0, -1 ):
                wx.CallAfter( self.parent.ReDrawWaitingTime, i )
                time.sleep(1)
                if self.ThreadIsRun == False:
                    break
        else:
            wx.CallAfter( self.parent.SetStartBtnLabel )

    #日志写入
    def WriteLog( self, strContent ):
        now = str( time.strftime("%Y-%m-%d %X", time.localtime()) )             #获取当前时间
        try:
            with open( "src/PubIng2012.log", "a+" ) as flog:
                flog.writelines( "%s : %s\r\n"%(now, strContent) )
        except:
            with open( "src/PubIng2012.log", "a+" ) as ferr:
                ferr.writelines( "%s : 用户 %s 的日志文件写入错误.\r\n"%(now, self.username) )

    def CheckIsStarIng( self, pubContent ):
        try:
            response = urllib.urlopen( 'http://home.cnblogs.com/ing/mobile/home' )
            ingTxt = response.readlines()
            for i in range(len(ingTxt)):
                if ingTxt[i].find(pubContent) != -1:
                    if ingTxt[i + 1].find('ing_icon_lucky') != -1:
                        return 1
                    else:
                        return 0
        except:
            return 0

    def LogoinCnblogs( self, name, pwd ):
        params_post = urllib.urlencode({
            '__EVENTTARGET': '',
            '__EVENTARGUMENT': '',
            '__VIEWSTATE': '/wEPDwULLTE1MzYzODg2NzZkGAEFHl9fQ29udHJvbHNSZXF1aXJlUG9zdEJhY2tLZXlfXxYBBQtjaGtSZW1lbWJlcm1QYDyKKI9af4b67Mzq2xFaL9Bt',
            '__EVENTVALIDATION': '/wEWBQLWwpqPDQLyj/OQAgK3jsrkBALR55GJDgKC3IeGDE1m7t2mGlasoP1Hd9hLaFoI2G05',
            'tbUserName' : name,
            'tbPassword' : pwd,
            'btnLogin'   :  '登录'
        })

        cookie = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
        urllib2.install_opener(opener)
        login_response = urllib2.urlopen( 'http://passport.cnblogs.com/login.aspx?', params_post )
        txt = login_response.read()     #读取返回数据

        if ( txt.find("用户名或密码错误") != -1 ):
            return '用户名或密码错误'
        elif txt.find("该用户不存在") != -1:
            return '该用户不存在。'
        elif txt.find("编辑个人资料") != -1:
            return 1
        else:
            return '未知错误, 无法登录!'


    def PubishIng( self, pubContent ):
        try:
            post_url = 'http://home.cnblogs.com/ajax/ing/Publish'
            params_post = urllib.urlencode({
                'content' : en( pubContent ) ,
                'publicFlag' : '1'
            })
            pubIng_response = urllib2.urlopen( post_url, params_post )
            responseInf = pubIng_response.read()
            #检测发布状态
            if ( responseInf.find("IsSuccess") != -1 ) and ( responseInf.find("true") != -1 ):
                return 1
            else:
                return 0
        except:
            return -1


class TaskBarIcon(wx.TaskBarIcon):
    ID_Play = wx.NewId()
    ID_About = wx.NewId()
    ID_Closeshow = wx.NewId()

    def __init__(self, frame):
        wx.TaskBarIcon.__init__(self)
        self.frame = frame
        self.SetIcon(wx.Icon(name='src/AppLogo.ico', type=wx.BITMAP_TYPE_ICO), u'PubIng2012')
        self.Bind(wx.EVT_TASKBAR_LEFT_DCLICK, self.OnTaskBarLeftDClick)
        self.Bind(wx.EVT_MENU, self.OnShow, id=self.ID_Play)
        self.Bind(wx.EVT_MENU, self.OnAbout, id=self.ID_About)
        self.Bind(wx.EVT_MENU, self.OnExitApp, id=self.ID_Closeshow)

    def OnTaskBarLeftDClick(self, event):
        if self.frame.IsIconized():
           self.frame.Iconize(False)
        if not self.frame.IsShown():
           self.frame.Show(True)
        self.frame.Raise()

    def OnShow(self, event):
        win32gui.ShowWindow( self.frame.Handle, 1 )
        win32gui.SetFocus(self.frame.Handle)

    def OnAbout(self, event):
        wx.CallAfter( self.frame.AboutPubIng2012, event )

    def OnExitApp(self,event):
        wx.CallAfter( self.frame.ExitApp )

    # 右键菜单
    def CreatePopupMenu(self):
        menu = wx.Menu()
        menu.Append(self.ID_Play, u'显示')
        menu.Append(self.ID_About, u'关于')
        menu.Append(self.ID_Closeshow, u'退出')
        return menu

class PubIng2012_MainFrame(wx.Frame):
    def __init__(self):
        self.username = ''
        self.password = ''
        #-----软件启动前的相关处理-----
        #self.CheckSrc()                                           #检查资源文件是否缺失
        #self.DisplaySize_X, self.DisplaySize_Y = wx.DisplaySize() #获取屏幕分辨率

        #-----初始化主界面-----
        wx.Frame.__init__(
            self,
            parent = None,
            id = -1,
            title = u"PubIng2012",
            size = (800, 550),
            style = wx.SYSTEM_MENU|wx.CAPTION|wx.MINIMIZE_BOX|wx.CLOSE_BOX
        )
        self.Center()
        #应用程序图标-----
        self.AppLogo = wx.Icon('src\AppLogo.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(self.AppLogo)
        #创建面板-----
        self.panel = wx.Panel(self)
        #最小化到系统托盘
        self.taskBarIcon = TaskBarIcon(self)

        #创建状态栏-----
        self.userStatus = self.CreateStatusBar()
        self.userStatus.SetFieldsCount(5)
        self.userStatus.SetStatusWidths([-5, -5, -5, -5, -6])
        #--
        self.userStatus.SetStatusText(u' 刷星状态: 未启动', 0)  #文字测试
        self.userStatus.SetStatusText(u' 成功发布: 0', 1)
        self.userStatus.SetStatusText(u' 发布失败: 0', 2)
        self.userStatus.SetStatusText(u' 得星统计: 0', 3)
        self.userStatus.SetStatusText(u' Copyright 2012, by ', 4)

        #设置静态框-----
        self.groupPubSeting = wx.StaticBox(
            self.panel,
            label = u'刷星设置',
            pos = ( 10, 10 ),
            size = ( 650, 120 ),
        )

        #-----发布内容设置
        self.groupPubContent = wx.StaticBox(
            self.panel,
            label = u'第一步:设置发布内容',
            pos = ( 50, 35 ),
            size = ( 200, 80 ),
        )
        #编辑提示信息
        rect = self.groupPubContent.Rect
        self.lblContentEditTip = wx.StaticText(
            self.panel,
            label = u'提示:每行一条闪存',
        )
        rect2 = self.lblContentEditTip.Rect
        self.lblContentEditTip.SetPosition(
            ( rect[0] + (rect[2] - rect2[2])/2,
            rect[1] + rect[3] -rect2[3] - 10 )
        )
        #编辑按钮-----
        self.btnEditPubContent = wx.Button(
            self.panel,
            label = u'编辑发布内容',
            size = ( 100, 30 ),
            pos = ( rect[0] + (rect[2] - 100)/2, rect[1] + 20 )
        )

        #-----发布频率设置
        self.groupPubInterval = wx.StaticBox(
            self.panel,
            label = u'第二步:设置刷星频率',
            pos = ( rect[0] + rect[2] + 60, rect[1] ),
            size = ( rect[2] + 100, rect[3] ),
        )

        rect = self.groupPubInterval.Rect
        self.lblSizeTip = wx.StaticText(
            self.panel,
            label = u'秒/闪',
            pos = ( rect[0] + 170, rect[1] + 25 )
        )
        #滑块
        self.sliderPubInterval = wx.Slider(
            self.panel,
            value = 60,
            minValue = 5,
            maxValue = 1024,
            pos = ( rect[0] + 10, rect[1] + 25 ),
            size = ( 280, -1 ),
            style = wx.SL_HORIZONTAL | wx.SL_LABELS
        )
        #开始刷星按钮
        self.btnStartPubIng = wx.Button(
            self.panel,
            label = u'开始刷星',
            size = ( 100, 55 ),
            pos = ( 680, 15 )
        )
        #查看日志按钮
        self.btnShowLog = wx.Button(
            self.panel,
            label = u'查看刷星日志',
            size = ( 100, 20 ),
            pos = ( 680, 85 )
        )
        #关于软件
        self.btnAboutPubIng2012 = wx.Button(
            self.panel,
            label = u'关于软件',
            size = ( 100, 20 ),
            pos = ( 680, 110 ),
        )

        #刷星列表
        #成功监听结果列表-----
        self.groupSucceedBox = wx.StaticBox(
            self.panel,
            label = u'刷星状态',
            pos = ( 10, 150 ),
            size = ( 775, 290 ),
        )
        self.lstSucceedResults = wx.ListCtrl(
            self.panel,
            pos = ( 20, 170 ),
            style = wx.LC_REPORT|wx.LC_HRULES|wx.LC_VRULES,
            size = ( 755, 260 )
        )
        self.lstSucceedResults.InsertColumn( col = 0, heading = u'发布时间', width = 150 )
        self.lstSucceedResults.InsertColumn( col = 1, heading = u'闪存内容', width = 420 )
        self.lstSucceedResults.InsertColumn( col = 2, heading = u'发布状态', width = 80 )
        self.lstSucceedResults.InsertColumn( col = 3, heading = u'是否有星', width = 80 )

        #距离下次发布时间
        self.lblWaiting = wx.StaticText(
            self.panel,
            label = u'距下一条闪存发布还需等待:',
            pos = ( 150, 465 )
        )
        self.lblWaiting.SetForegroundColour( ( 0, 0, 0 ) )
        font = wx.Font( 11, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False )
        self.lblWaiting.SetFont(font)
        #显示秒数
        self.lblShowTime = wx.StaticText(
            self.panel,
            label = u'00秒',
            pos = ( 350, 450 )
        )
        self.lblShowTime.SetForegroundColour( ( 0, 190, 0 ) )
        font = wx.Font( 28, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False )
        self.lblShowTime.SetFont(font)
        #暂时隐藏等待时间状态
        self.lblWaiting.Hide()
        self.lblShowTime.Hide()

        #底部连接
        self._lblLinkx86 = wx.HyperlinkCtrl(
            self.userStatus,
            id = -1,
            label = u'wid',
            url = u'http://www.cnblogs.com/mr-wid/',
            pos = (735, 5)
        )

        #一次性定时器
        self.timerShowLoginDlg = wx.Timer(self)
        self.timerShowLoginDlg.Start( milliseconds = -1, oneShot = True )

        #--线程
        self.ThreadWork = None

        #发布状态数据
        self.AppStatus = ''
        self.PubSucceed = 0
        self.PubFailed = 0
        self.StarIng = 0

        #------事件绑定------
        self.Bind( wx.EVT_CLOSE, self.ExitApp )
        self.Bind( wx.EVT_BUTTON, self.EditIngText, self.btnEditPubContent  )   #编辑闪存发布内容
        self.Bind( wx.EVT_BUTTON, self.AboutPubIng2012, self.btnAboutPubIng2012)#关于软件
        self.Bind( wx.EVT_TIMER, self.OnTimerLogin, self.timerShowLoginDlg )    #登录对话框
        self.Bind( wx.EVT_BUTTON, self.StartPubIng, self.btnStartPubIng )       #开始刷星
        self.Bind( wx.EVT_BUTTON, self.ShowLogs, self.btnShowLog )              #查看日志文件

        self.Bind(wx.EVT_ICONIZE, self.OnIconfiy)                               #最小化到系统托盘

    def StartPubIng( self, event ):
        if self.btnStartPubIng.GetLabel() == u'开始刷星':
            sliderValue = self.sliderPubInterval.GetValue()
            self.ThreadWork = ThreadWork( self, self.username, self.password, sliderValue )
            self.ThreadWork.start()
            self.btnStartPubIng.SetLabel(u'停止刷星')
            self.lblWaiting.Show()
            self.lblShowTime.Show()
            self.lblShowTime.SetLabel( str(sliderValue) + u'秒' )
            self.userStatus.SetStatusText(u' 刷星状态: 正在刷星...', 0)
        else:
            self.ThreadWork.stop()


    def ExitApp( self, event = None ):
        self.taskBarIcon.Destroy()
        self.Destroy()

    def SetUserInfo( self, name, pwd ):
        self.username = name
        self.password = pwd

    #编辑闪存内容
    def EditIngText( self, event ):
        '''
        Function: 编辑闪存发布内容
        NOTE: EdtIngText(self, event) -> None
        '''
        with open( 'src/PubIng2012_IngContent.txt', 'a+' ) as f:
            win32api.ShellExecute( self.Handle, "open", "src\PubIng2012_IngContent.txt", "", "", 1 )

    def ShowLogs( self, event ):
        with open( 'src/PubIng2012.log', 'a+' ) as f:
            win32api.ShellExecute( self.Handle, "open", "src\PubIng2012.log", "", "", 1 )

    #关于软件
    def AboutPubIng2012( self, event ):
        dlg = PubIng2012_AboutDlg.AboutDlg()
        dlg.ShowModal()

    def ShowErrors( self, info ):
        wx.MessageBox( info, u'错误', wx.OK )

    #登录对话框
    def OnTimerLogin( self, event ):
        loginDlg = PubIng2012_LoginCnblogsDlg.LoginCnblogsDlg(self)
        loginDlg.ShowModal()

    def ReDrawWaitingTime( self, time ):
        self.lblShowTime.SetLabel( u'%s秒'%str(time) )

    def SetStartBtnLabel( self ):
        self.btnStartPubIng.SetLabel( u'开始刷星' )
        self.lblWaiting.Hide()
        self.lblShowTime.Hide()
        self.userStatus.SetStatusText(u' 刷星状态: 未启动', 0)

    def PrintS( self, s ):
        print s

    def ReDrawListCtrl( self, content ):
        try:
            index = self.lstSucceedResults.ItemCount
            self.lstSucceedResults.InsertStringItem( index, content[0] )
            self.lstSucceedResults.SetStringItem( index, 1, content[1] )
            self.lstSucceedResults.SetStringItem( index, 2, content[2] )
            self.lstSucceedResults.SetStringItem( index, 3, content[3] )
            if content[2] == u'发布成功':
                self.ReSetPubSucceedStatus()
            else:
                self.ReSetPubFailedStatus()
            if content[3] == u'这是幸运闪':
                self.ReSetStarIngStatus()
        except:
            pass

    def ReSetPubSucceedStatus( self ):
        self.PubSucceed += 1
        self.userStatus.SetStatusText(u' 成功发布: %d'%self.PubSucceed, 1)
    def ReSetPubFailedStatus( self ):
        self.PubFailed += 1
        self.userStatus.SetStatusText(u' 发布失败: %d'%self.PubFailed, 2)
    def ReSetStarIngStatus( self ):
        self.StarIng += 1
        self.userStatus.SetStatusText(u' 得星统计: %d'%self.StarIng, 3)

    #最小化到托盘事件
    def OnHide(self, event):
        self.Hide()
    def OnIconfiy(self, event):
        self.Hide()
        event.Skip()


def main():
    PubIng2012 = wx.PySimpleApp()
    MainFrame = PubIng2012_MainFrame()
    MainFrame.Show()
    PubIng2012.MainLoop()

if __name__ == '__main__':
    main()