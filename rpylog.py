"""
Copyright (c) 2021 Lukas Pfeifer

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and 
associated documentation files (the "Software"), 
to deal in the Software without restriction, including without limitation the rights 
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, 
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, 
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import socket
import datetime
import os
from enum import Enum


class rpylog:
    """
    Main class for rsyslog communication.
    
    For further information about syslog protocol see RFC 5424
    https://tools.ietf.org/html/rfc5424
    """

    class property:
        Tag = None
        Value = None

        def __init__(self, tag, value):
            self.Tag = tag
            self.Value = value

    __socket = None
    __socketKind = None
    __serverAddress = None
    __port = None

    MessageTemplate = "<%PRI%>%VERSION% %TIMESTAMP% %HOSTNAME% %APP-NAME% %PROCID% %MSGID% %MSG%"
    
    SyslogVersion = property("%VERSION%", 1)
    AppName = property("%APP-NAME%", None)
    Hostname = property("%HOSTNAME%", None)
    ProcessId = property("%PROCID%", os.getpid())
        
    class SEVERTIY(Enum):
        EMERGENCY = 0
        ALERT = 1
        CRITICAL = 2
        ERROR = 3
        WARNING = 4
        NOTICE = 5
        INFORMATIONAL = 6
        DEBUG = 7

    class FACILITY(Enum):
        KERNEL_MESSAGES = 0
        USER_LEVEL_MESSAGES = 1
        MAIL_SYSTEM = 2
        SYSTEM_DEMONS = 3
        SEC_AUTH_MESSAGES = 4
        INTERNAL_SYSLOG = 5
        LINE_PRINTER_SUBSYSTEM = 6
        NETWORK_NEWS_SUBSYSTEM = 7
        UUCP_SUBSYSTEM = 8
        CLOCK_DAEMON = 9
        SEC_AUTH_MESSAGES_2 = 10
        FTP_DAEMON = 11
        NTP_SUBSYSTEM = 12
        LOG_AUDIT = 13
        LOG_ALERT = 14
        CLOCK_DAEMON_2 = 15
        LOCAL_0 = 16
        LOCAL_1 = 17
        LOCAL_2 = 18
        LOCAL_3 = 19
        LOCAL_4 = 20
        LOCAL_5 = 21
        LOCAL_6 = 22
        LOCAL_7 = 23

    def __init__(self, serverAddress, port, socketKind):
        """
        :param socketKind: Socket type like socket.SOCK_STREAM (TCP) or socket.SOCK_DGRAM (UDP) etc.
        """
        self.serverAddress = serverAddress
        self.port = port
        self.socketKind = socketKind
        self.__initSocket()

    def __initSocket(self):
        self.socket = socket.socket(socket.AF_INET, self.socketKind, 0)

    def Open(self):
        self.socket.connect((self.serverAddress, self.port))

    def Close(self):
        self.socket.close()


    def SetMessageTemplate(self, template):
        self.MessageTemplate = template

    def SetSyslogVersion(self, version):
        self.SyslogVersion.Value = version

    def SetAppname(self, appname):
        self.AppName.Value = appname
    
    def SetHostname(self, hostname):
        self.Hostname.Value = hostname
    
    
    def Emergency(self, msg, msg_id=None):
        self.__writeLog(msg, self.MessageTemplate, rpylog.FACILITY.LOCAL_0,
                        rpylog.SEVERTIY.EMERGENCY, msg_id)

    def Alert(self, msg, msg_id=None):
        self.__writeLog(msg, self.MessageTemplate, rpylog.FACILITY.LOCAL_0,
                        rpylog.SEVERTIY.ALERT, msg_id)

    def Critical(self, msg, msg_id=None):
        self.__writeLog(msg, self.MessageTemplate, rpylog.FACILITY.LOCAL_0,
                        rpylog.SEVERTIY.CRITICAL, msg_id)

    def Error(self, msg, msg_id=None):
        self.__writeLog(msg, self.MessageTemplate, rpylog.FACILITY.LOCAL_0,
                        rpylog.SEVERTIY.ERROR, msg_id)

    def Warning(self, msg, msg_id=None):
        self.__writeLog(msg, self.MessageTemplate, rpylog.FACILITY.LOCAL_0,
                        rpylog.SEVERTIY.WARNING, msg_id)

    def Notice(self, msg, msg_id=None):
        self.__writeLog(msg, self.MessageTemplate, rpylog.FACILITY.LOCAL_0,
                        rpylog.SEVERTIY.NOTICE, msg_id)

    def Informational(self, msg, msg_id=None):
        self.__writeLog(msg, self.MessageTemplate, rpylog.FACILITY.LOCAL_0,
                        rpylog.SEVERTIY.INFORMATIONAL, msg_id)

    def Debug(self, msg, msg_id=None):
        self.__writeLog(msg, self.MessageTemplate, rpylog.FACILITY.LOCAL_0,
                        rpylog.SEVERTIY.DEBUG, msg_id)

    def __writeLog(self, msg, template, facility, severity, msg_id=None):
        
        priority = rpylog.property("%PRI%", self.__calcPriority(severity, facility))
        timestamp = rpylog.property("%TIMESTAMP%", str(datetime.datetime.now()))
        messageId = rpylog.property("%MSGID%", msg_id)
        message = rpylog.property("%MSG%", msg)

        properties = [priority,
                      self.SyslogVersion,
                      timestamp,
                      messageId,
                      message,
                      self.AppName,
                      self.Hostname,
                      self.ProcessId]

        final = self.__createFinalMessage(properties)

        encoded = final.encode()
        self.socket.send(encoded)

    def __calcPriority(self, severity, facility):
        if not severity:
            return None

        if not facility:
            return None

        return (facility.value * 8) + severity.value

    def __createFinalMessage(self, properties):
        
        result = self.MessageTemplate
        
        for prop in properties:
            if not prop.Value:
                prop.Value = "-"
                
            result = result.replace(prop.Tag, str(prop.Value))
        
        return result