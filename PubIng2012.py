#-------------------------------------------------------------------------------
# Name:        PubIng2012.py
# Purpose:
#
# Author:      wid
#
# Created:     27-11-2012
# Copyright:   (c) wid 2012
# Licence:     GNU GPL
#-------------------------------------------------------------------------------

import wx
import PubIng2012_MainFrame

def main():
    app = wx.PySimpleApp()
    frame = PubIng2012_MainFrame.PubIng2012_MainFrame()
    frame.Show()
    app.MainLoop()

if  __name__ == '__main__':
    main()
