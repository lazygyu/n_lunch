# -*- coding: utf-8 -*-
def openAnything(source):            
    """URI, filename, or string --> stream

    (URL, 지역 또는 네트워크 파일에 대한 경로이름, 또는 실제 데이터를 문자열로 등등)
    이 함수는 해석기를 아무 입력이나 받도록 정의하고, 
    일관된 형태로 다룰 수 있도록 해준다. 
    반환된 객체는 기본적인 stdio 읽기 메소드 (read, readline, readlines)를, 
    모두 갖추고 있다고 보증된다.
    처리가 끝나면 그냥 그 객체에 .close()를 요청하면 된다.
    
    예제:
    >>> from xml.dom import minidom
    >>> sock = openAnything("http://localhost/kant.xml")
    >>> doc = minidom.parse(sock)
    >>> sock.close()
    >>> sock = openAnything("c:\\inetpub\\wwwroot\\kant.xml")
    >>> doc = minidom.parse(sock)
    >>> sock.close()
    >>> sock = openAnything("<ref id='conjunction'><text>and</text><text>or</text></ref>")
    >>> doc = minidom.parse(sock)
    >>> sock.close()
    """
    if hasattr(source, "read"):
        return source

    if source == '-':
        import sys
        return sys.stdin

    # (소스가 http나 ftp 또는 파일 URL이라면) urllib로 열기를 시도한다.
    import urllib                         
    try:                                  
        return urllib.urlopen(source)     
    except (IOError, OSError):            
        pass                              
    
    # (소스가 경로이름이라면) 고유의 열기 함수로 열기를 시도한다.
    try:                                  
        return open(source)               
    except (IOError, OSError):            
        pass                              
    
    # 소스를 문자열로 취급한다
    import StringIO                       
    return StringIO.StringIO(str(source))