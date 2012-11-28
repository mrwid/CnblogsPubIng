#coding:utf-8
#-------------------------------------------------------------------------------
# Name:        PubIng2012_LoginCnblogsDlg.py
# Purpose:
#
# Author:      wid
#
# Created:     26-11-2012
# Copyright:   (c) wid 2012
# Licence:     GNU GPL
#-------------------------------------------------------------------------------

import wx
import base64
import urllib
import urllib2
import cookielib


def en(x):
    return x.encode('utf-8')

def cn(x):
    return x.decode('utf-8')


def LogoinCnblogs( name, pwd ):
    try:
        params_post = urllib.urlencode({
            '__EVENTTARGET': '',
            '__EVENTARGUMENT': '',
            '__VIEWSTATE': r'/wEPDwULLTE1MzYzODg2NzZkGAEFHl9fQ29udHJvbHNSZXF1aXJlUG9zdEJhY2tLZXlfXxYBBQtjaGtSZW1lbWJlcm1QYDyKKI9af4b67Mzq2xFaL9Bt',
            '__EVENTVALIDATION': r'/wEWBQLWwpqPDQLyj/OQAgK3jsrkBALR55GJDgKC3IeGDE1m7t2mGlasoP1Hd9hLaFoI2G05',
            'tbUserName': en(name),
            'tbPassword': en(pwd),
            'btnLogin'  : '登录'
        })

        cookie = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
        urllib2.install_opener(opener)
        login_response = urllib2.urlopen( 'http://passport.cnblogs.com/login.aspx?', params_post )
        txt = login_response.read()     #读取返回数据

        if ( txt.find("用户名或密码错误") != -1 ):
            return u'用户名或密码错误'
        elif txt.find("该用户不存在") != -1:
            return u'该用户不存在。'
        elif txt.find("编辑个人资料") != -1:
            return 1
        else:
            return u'未知错误, 无法登录!'
    except:
        return u'未知错误, 无法登录!'

class LoginCnblogsDlg(wx.Dialog):
    def __init__( self, parent = None ):
        self.parane = parent
        wx.Dialog.__init__(
            self,
            parent = parent,
            title = u'用户登录 - 博客园用户中心',
            size = (400, 300),
        )
        #-----彷web登录页
        #登录提示
        self.lblLoginTip = wx.StaticText(
            self,
            label = u'登录到博客园',
            pos = ( 60, 20 )
        )
        self.lblLoginTip.SetForegroundColour( ( 153, 0, 68 ) )
        font = wx.Font( 15, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False )
        font.SetWeight(wx.BOLD)
        self.lblLoginTip.SetFont(font)
        #"立即注册"提示
        rect = self.lblLoginTip.Rect
        self.lblLinkRegister = wx.HyperlinkCtrl(
            self,
            id = -1,
            label = u'立即注册',
            url = u'http://passport.cnblogs.com/register.aspx',
            pos = ( rect[0] + rect[2] + 10, rect[1] + 8 )
        )
        self.lblLinkRegister.SetForegroundColour( (0, 44, 153) )
        #--用户名输入提示
        self.lblUserName = wx.StaticText(
            self,
            label = u'用户名',
            pos = ( rect[0], rect[1] + rect[3] + 25 )
        )
        self.lblUserName.SetForegroundColour( ( 153, 153, 153 ) )
        font = wx.Font( 9, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False )
        font.SetWeight(wx.BOLD)
        self.lblUserName.SetFont(font)
        #用户名输入框
        rect = self.lblUserName.Rect
        self.txtUserName = wx.TextCtrl(
            self,
            size = (200, -1),
            pos = (rect[0], rect[1] + rect[3] + 5),
            value = ''
        )
        font = wx.Font( 10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False )
        self.txtUserName.SetFont(font)
        #找回用户名提示
        rect = self.txtUserName.Rect
        self.lblGetUsername = wx.HyperlinkCtrl(
            self,
            id = -1,
            label = u'找回用户名',
            url = u'http://passport.cnblogs.com/GetUsername.aspx',
            pos = ( rect[0] + rect[2] + 5, rect[1] + 5 )
        )
        #--密码输入提示
        rect = self.txtUserName.Rect
        self.lblPassWord = wx.StaticText(
            self,
            label = u'密码',
            pos = ( rect[0], rect[1] + rect[3] + 20 )
        )
        self.lblPassWord.SetForegroundColour( ( 153, 153, 153 ) )
        font = wx.Font( 9, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False )
        font.SetWeight(wx.BOLD)
        self.lblPassWord.SetFont(font)
        #密码输入框
        rect = self.lblPassWord.Rect
        self.txtPassWord = wx.TextCtrl(
            self,
            size = (200, -1),
            pos = (rect[0], rect[1] + rect[3] + 5),
            value = '',
            style = wx.TE_PASSWORD
        )
        font = wx.Font( 10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False )
        self.txtPassWord.SetFont(font)
        #找回密码提示
        rect = self.txtPassWord.Rect
        self.lblGetPassword = wx.HyperlinkCtrl(
            self,
            id = -1,
            label = u'找回密码',
            url = u'http://passport.cnblogs.com/GetMyPassword.aspx',
            pos = ( rect[0] + rect[2] + 5, rect[1] + 5 )
        )

        #--记住密码
        rect = self.txtPassWord.Rect
        self.chkRemberPwd = wx.CheckBox(
            self,
            label = u'保存密码',
            pos = (rect[0], rect[1] + rect[3] + 15)
        )
        #--登录
        rect = self.chkRemberPwd.Rect
        self.btnLogin = wx.Button(
            self,
            label = u"登 录",
            pos = (rect[0], rect[1] + rect[3] + 10),
            size = (100, 35)
        )
        self.btnLogin.SetForegroundColour( (153, 0, 68) )
        font = wx.Font( 14, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False )
        font.SetWeight(wx.BOLD)
        self.btnLogin.SetFont(font)
        #登录错误提示
        rect = self.btnLogin.Rect
        self.lblError = wx.StaticText(
            self,
            label = u'',
            pos = ( rect[0], rect[1] + rect[3] + 5 )
        )
        self.lblError.SetForegroundColour( (255, 0, 0) )
        font = wx.Font( 9, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False )
        font.SetWeight(wx.BOLD)
        self.lblError.SetFont(font)

        #定时器, 从本地读取用户信息
        self.timerReadUserInfo = wx.Timer(self)
        self.timerReadUserInfo.Start( milliseconds = -1, oneShot = True )

        #--窗口关闭事件绑定
        self.Bind( wx.EVT_TIMER, self.ReadUserInfo, self.timerReadUserInfo )    #定时器, 读取用户信息
        self.Bind( wx.EVT_CLOSE, self.ExitApp )                                 #绑定退出事件
        self.Bind( wx.EVT_BUTTON, self.Login, self.btnLogin )                   #登录事件
        self.Bind( wx.EVT_CHECKBOX, self.RemmberPwd, self.chkRemberPwd )        #绑定保存密码

    #读取用户信息
    def ReadUserInfo( self, event ):
        try:
            with open( 'src/setting.st', 'r' ) as f:
                info = f.readlines()
                username = base64.decodestring(info[0])[3:-1-2]
                password = base64.decodestring(info[1])[3:-1-2]
                self.txtUserName.SetValue( username )
                self.txtPassWord.SetValue( password )
                self.chkRemberPwd.SetValue( True )
        except:
            pass

    #退出程序
    def ExitApp( self, event ):
        wx.CallAfter(self.parane.ExitApp)       #关联主窗口, 子窗口关闭时主窗口也关闭
        self.Destroy()

    #对字符串进行base64编码转化进行伪加密
    def base64ToPwd( self, strString ):
        strString = 'qqa' + strString + 'wid'             #在待加密文本中插入字符
        return base64.encodestring( en(strString) )             #对自身进行base64编码

    #记住密码
    def RemmberPwd( self, event ):
        if self.chkRemberPwd.GetValue() == True:
            username = self.txtUserName.Value
            password = self.txtPassWord.Value
            username = self.base64ToPwd( username )
            password = self.base64ToPwd( password )
            with open( 'src/setting.st', 'w' ) as f:
                f.writelines(username)
                f.writelines(password)
        else:
            with open( 'src/setting.st', 'w' ) as f:
                f.close()

    #登录测试
    def Login( self, event ):
        self.RemmberPwd( event )
        username = self.txtUserName.GetValue()
        password = self.txtPassWord.GetValue()
        if username == '' or username.isspace() == True:
            wx.MessageBox( u'用户名不能为空', u'登录提示', wx.OK )
            return
        if password == '':
            wx.MessageBox( u'密码不能为空', u'登录提示', wx.OK )
            return
        status = LogoinCnblogs( username, password )
        if status == 1:
            wx.CallAfter( self.parane.SetUserInfo, username, password )
            self.Destroy()
            return
        else:
            self.lblError.SetLabel( status )


def test():
    app = wx.PySimpleApp()
    dlg = LoginCnblogsDlg()
    dlg.ShowModal()

if __name__ == '__main__':
    test()
