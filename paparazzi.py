#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
                  GNU LESSER GENERAL PUBLIC LICENSE
                       Version 2.1, February 1999

Copyright (C) 1991, 1999 Free Software Foundation, Inc.
51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
Everyone is permitted to copy and distribute verbatim copies
of this license document, but changing it is not allowed.

[This is the first released version of the Lesser GPL.  It also counts
 as the successor of the GNU Library Public License, version 2, hence
 the version number 2.1.]
 
http://www.gnu.org/licenses/lgpl-2.1.txt

This is a derived work from CutyCapt: http://cutycapt.sourceforge.net/

////////////////////////////////////////////////////////////////////
//
// CutyCapt - A Qt WebKit Web Page Rendering Capture Utility
//
// Copyright (C) 2003-2010 Bjoern Hoehrmann <bjoern@hoehrmann.de>
//
// This program is free software; you can redistribute it and/or
// modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// $Id$
//
////////////////////////////////////////////////////////////////////

"""

import sys
import argparse
import httplib
import urlparse
from PyQt4 import QtCore, QtGui, QtWebKit

class Capturer(object):
    """A class to capture webpages as images"""

    def __init__(self, url, filename, size):
        self.url = url
        self.filename = filename
        self.size = size
        self.saw_initial_layout = False
        self.saw_document_complete = False

    def loadFinishedSlot(self):
        self.saw_document_complete = True
        if self.saw_initial_layout and self.saw_document_complete:
            self.doCapture()
            
    def _get_server_status_code(self):
        host, path = urlparse.urlparse(self.url)[1:3]
        conn = httplib.HTTPConnection(host)
        conn.request('HEAD', path)
        try:
            conn = httplib.HTTPConnection(host)
            conn.request('HEAD', path)
            return conn.getresponse().status
        except StandardError:
            return None
            
    def checkURL(self):
        good_codes = [httplib.OK, httplib.FOUND, httplib.MOVED_PERMANENTLY]

        try:
            return self._get_server_status_code() in good_codes
        except StandardError:
            return False

    def initialLayoutSlot(self):
        self.saw_initial_layout = True
        if self.saw_initial_layout and self.saw_document_complete:
            self.doCapture()

    def capture(self):
        """Captures url as an image to the file specified"""
        self.wb = QtWebKit.QWebPage()
        self.wb.mainFrame().setScrollBarPolicy(
            QtCore.Qt.Horizontal, QtCore.Qt.ScrollBarAlwaysOff)
        self.wb.mainFrame().setScrollBarPolicy(
            QtCore.Qt.Vertical, QtCore.Qt.ScrollBarAlwaysOff)

        self.wb.loadFinished.connect(self.loadFinishedSlot)
        self.wb.mainFrame().initialLayoutCompleted.connect(
            self.initialLayoutSlot)

        self.wb.mainFrame().load(QtCore.QUrl(self.url))

    def doCapture(self):
        
        qt_size = QtCore.QSize(int(self.size[0]), int(self.size[1]))
        #qt_size = QtCore.QSize(self.wb.mainFrame().contentsSize())

        self.wb.setViewportSize(qt_size)

        img = QtGui.QImage(self.wb.viewportSize(), QtGui.QImage.Format_ARGB32)
        painter = QtGui.QPainter(img)
        self.wb.mainFrame().render(painter)
        painter.end()
        img.save(self.filename)
        QtCore.QCoreApplication.instance().quit()

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='Capture a screenshot in PNG format from a website.')
    parser.add_argument('-u', '--url', metavar='address', type=str, help='An URL', required=True)
    parser.add_argument('-f', '--filename', metavar='filename', type=str, help='Image filename', required=True)
    parser.add_argument('-s', '--size', metavar='width height', type=str, nargs=2, help='image size in pixels', required=True)
    #parser.add_argument('-r', '--resolution', metavar='width height', type=str, nargs=2, help='browser resolution in pixels', default='1024 768')
    args = parser.parse_args()
    
    app = QtGui.QApplication(sys.argv)
    c = Capturer(str(args.url), str(args.filename), args.size)

    if c.checkURL():
        c.capture()
        app.exec_()
    else:
        print 'error: Invalid URL'