# rpylog
Simple rsyslog client written in python, supporting custom templates, standard properties and multiple protocols.


# Example

```python
def example():
    log = rpylog("github.com", 80, socket.SOCK_STREAM)
    
    log.SetSyslogVersion(1)
    log.SetAppname("TestApp")
    log.SetHostname("justme")
    
    # Use custom template instead of default
    log.SetMessageTemplate("<%PRI%>%MSG%")
    
    """
    Default: <%PRI%>%VERSION% %TIMESTAMP% %HOSTNAME% %APP-NAME% %PROCID% %MSGID% %MSG%
    """

    log.Open()

    log.Emergency("Holy s**t\n")
    log.Alert("Oh my god...\n")
    log.Critical("Pf okay, it's fine...\n")
    log.Error("Nah...\n")
    log.Warning("Hehe\n")
    log.Notice("Nope\n")
    log.Informational("Just some info\n")
    log.Debug("Who reads this anyways?\n")
    
    log.Close()
```
