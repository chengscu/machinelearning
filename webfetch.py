#!/usr/bin/env python

import os
import re
import sys
from urlparse import urlparse          # parse url
from urlparse import urljoin           # join url
import urllib2                         # read web pages


##
## From this python script we demostrate some of the 
## basics of python, including
## - os.path.isfile
## - os.path.isdir
## - os.path.dirname
## - os.path.basename
## - os.path.join
## - os.path.normpath      # cllapse the path
## - os.path.relpath       # relative path
##
## - 'set' data structure
## - myset = set([])       # instantiated from a list
## - myset.add(elem)
## - for e in myset ...    # loop over a set
##
## - re.findall(pattern, text)      # return a list of string
## - re.split(pattern, text)        # return a list of string 
## - re.sub(pattern, replacement, text)   # return string
## - re.sub(pattern, repl_callback, text) # return string
## - MatchObject.group(0|1|2...)
## - if re.search(pattern, text): ...   # search through text
## - if re.match(pattern, text): ...    # search only at the beginning of text
##
## - try: ... except: ...
## - raise StandardError, 'info'
##
## - urlparse(url)
## - urlparse(url).scheme|netloc|path|...
## - urljoin(base, sub)


"""
Brief: Extract href from a html page.
Input: An html page.
Input: pattern (optional)
Return: Href list.
"""
def extract_href(htmlpage, pattern = None) :
    assert os.path.isfile(htmlpage)
    f = open(htmlpage)
    content = f.read()
    href_pattern = '[Hh][Rr][Ee][Ff][\s]*=[\s]*[\"\']*([^\"\'\s>]+)[\"\'\s>]' # note the 'group' in the pattern
    if pattern == None:
        ret = re.findall(href_pattern, content)
    else:
        ret = []
        match = re.findall(href_pattern, content)
        for m in match:
            if re.match(pattern, m):
                ret.append(m)
    return ret 

"""
Brief: Extract src reference from a html page.
Input: An html page.
Return: Src reference list.
"""
def extract_src(htmlpage) :
    assert os.path.isfile(htmlpage)
    f = open(htmlpage)
    content = f.read()
    pattern = '[Ss][Rr][Cc][\s]*=[\s]*[\"\']*([^\"\'\s>]+)[\"\'\s>]' # note the 'group' in the pattern
    match = re.findall(pattern, content)
    return match

"""
Brief: Download a web page or web file.
Input: 
    1.  Url of the web page/file.
    2.  Max try.
Return: 
    Local path to the page/file or None if fail.
Note: Local path is 'cwd' + 'netloc' + 'path'.
      If the url points to a directory instead of
      file, then the web page will be stored at 'index.html'.
"""
def download_page(url, maxtry = 3) :
    if len(urlparse(url).netloc) == 0 or len(urlparse(url).path) == 0 :
        printf('Skip invalid url: %s'%(url))
        return None

    path = urlparse(url).netloc +  urlparse(url).path
    if path.endswith('/') :
        path = path + 'index.html'
    path = os.path.normpath(path) # for cross platform

    # we must guarantee that the path do not go beyond current directory
    assert os.path.relpath(path).find('..') == -1

    if os.path.isfile(path) :
        return path 
    if os.path.isdir(path) :
        return None 
    if maxtry <= 0 :
        return None

    try :
        request = urllib2.Request(url, headers={'User-Agent':"Magic Browser"})
        webpage = urllib2.urlopen(request)  # return a file like object
    except :
        maxtry = maxtry - 1
        if maxtry <= 0 :
            print 'Fail in downloading \'' + url + '\'.'
            return None
        else :
            return download_page(url, maxtry)

    directory = os.path.dirname(path)
    if os.path.isfile(directory): # TODO
        return None
    if not os.path.isdir(directory) :
        os.makedirs(directory)
    suffix = path.split('.')
    suffix = suffix[len(suffix) - 1]
    if suffix in ['pdf', 'doc', 'docx', 'ppt', 'pptx', 'png', 'jpeg']:
        f = open(path, 'wb')
    else :
        f = open(path, 'w')
    web_content = webpage.read()
    f.write(web_content)
    f.close()
    print '\'' + path + '\' generated.'
    return path

__url = None
def replace_reference_abs(matchobj) :
    global __url
    assert(__url != None)
    rel = os.path.relpath(matchobj.group(3), \
            os.path.dirname(urlparse(__url).netloc + urlparse(__url).path))
    #if matchobj.group(3).endswith('/') :
        #rel = rel + '/index.html'
    return matchobj.group(1) + '\"' + rel + '\"'

def replace_reference_base(matchobj) :
    global __url
    assert(__url != None)
    ref = urlparse(__url).netloc + matchobj.group(2)
    rel = os.path.relpath(ref, \
            os.path.dirname(urlparse(__url).netloc + urlparse(__url).path))
    #if matchobj.group(2).endswith('/') :
        #rel = rel + '/index.html'
    return matchobj.group(1) + '\"' + rel + '\"'

def convert_src_links(htmlpage, url) :
    global __url
    assert os.path.isfile(htmlpage)
    fin = open(htmlpage, 'r')
    text = fin.read()
    fin.close()
    __url = url
    pattern = '([Ss][Rr][Cc][\s]*=[\s]*)\"([Hh][Tt][Tt][Pp]://)([^"]+)\"'
    text = re.sub(pattern, replace_reference_abs, text)
    pattern = '([Ss][Rr][Cc][\s]*=[\s]*)\"(/[^"]+)\"'
    text = re.sub(pattern, replace_reference_base, text)
    __url = None
    
    fout = open(htmlpage, 'w')
    fout.write(text)
    fout.close()

def convert_href_links(htmlpage, url) :
    global __url
    assert os.path.isfile(htmlpage)
    print('converting ' + htmlpage)
    fin = open(htmlpage, 'r')
    text = fin.read()
    fin.close()
    __url = url
    pattern = '([Hh][Rr][Ee][Ff][\s]*=[\s]*)\"([Hh][Tt][Tt][Pp]://)([^"]+)\"'
    text = re.sub(pattern, replace_reference_abs, text)
    pattern = '([Hh][Rr][Ee][Ff][\s]*=[\s]*)\"(/[^"]+)\"'
    text = re.sub(pattern, replace_reference_base, text)
    __url = None
    
    fout = open(htmlpage, 'w')
    fout.write(text)
    fout.close()

"""
Download the source reference(src) within a webpage.
Input :
    1. htmlpage (string), local path to the web page.
    2. url (string), uniform resource locator.
    3. inner_only (boolean), wether only to download reference with
       the same netloc as the given 'url'.
    4. convert_links (boolean), wether convert links in 'htmlpage'.
Output :
    Qualified reference will be download.
    The url of downloaded hsrc
Return :
    List of url of downloaded pages.
Invariant:
    If 'convert_links' is true, then links within the html page
    will be converted to local relative path.
"""
def download_src(htmlpage, url, inner_only = True, convert_links = True) :
    assert os.path.isfile(htmlpage)
    sources = extract_src(htmlpage)
    srcset = set([])
    for src in sources :
        src = urljoin(url, src)
        if inner_only and (urlparse(src).netloc != urlparse(url).netloc) :
            continue
        srcset.add(src)
    srcpages = []
    for src in srcset :
        path = download_page(src)
        if path != None :
            srcpages.append(src)
    if(convert_links) :
        convert_src_links(htmlpage, url)
    return srcpages

"""
Download the hyper reference(href) within a webpage.
Input :
    1. htmlpage (string), local path to the web page.
    2. url (string), uniform resource locator.
    3. pattern (string), selected pattern in href
    4. inner_only (boolean), wether only to download reference with
       the same netloc as the given 'url'.
    5. convert_links (boolean), wether convert links in 'htmlpage'.
Output :
    Qualified reference will be download.
    The url of downloaded href
Invariant:
    If 'convert_links' is true, then links within the html page
    will be converted to local relative path.
"""
def download_href(htmlpage, url, pattern=None, inner_only = True, convert_links = True) :
    assert os.path.isfile(htmlpage)
    href = extract_href(htmlpage, pattern)
    refset = set([])
    for ref in href :
        if ref.startswith('#') : # fragment within the htmlpage
            continue
        ref = urljoin(url, ref)
        if inner_only and (urlparse(ref).netloc != urlparse(url).netloc) :
            continue
        # remove the url fragment
        ref = ref.split('#') 
        ref = ref[0]
        refset.add(ref)
    reflist = []
    for ref in refset :
        path = download_page(ref)
        if path != None :
            reflist.append(ref)
    if(convert_links) :
        convert_href_links(htmlpage, url)
    return reflist

def url_smart_complement(url) :
    if url.find('/') == -1 :
        return 'http://' + url + '/'
    if url.find('://') == -1 :
        url = 'http://' + url
    if len(urlparse(url).path) == 0 :
        url = url + '/'
    if not url.endswith('/') :
        last = url.split('/')
        last = last[len(last) - 1]
        if last.find('.') == -1 :
            url = url + '/'
    return url

"""
Fetch web pages.
Note :
    depth == 0: download only the page
    depth == 1: download the page and the hyper reference therein
    depth == 2: download reference of reference
    depth == 3: ...
"""
def webfetch(url, depth=0, local=True) :
    page = download_page(url)
    if page != None and depth > 0 :
        srclist = download_src(page, url, True)
        reflist = download_href(page, url, inner_only=local)
        for ref in reflist :
            if ref.endswith('/') or ref.endswith('html') :
                webfetch(ref, depth - 1, local)
    return page

url="https://www.tensorflow.org/extend/architecture"
webfetch(url=url,depth=1)
