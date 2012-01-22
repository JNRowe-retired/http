from urlparse import urlunparse as urlimplode, urlparse as urlexplode
from urlparse import parse_qsl as queryexplode, urljoin
from urllib import urlencode as queryimplode
import re


class Url(object):
    __author__ = "Damien 'bl0b' Leroux <damien.leroux@gmail.com>"

    """Handles URLs.

    Construct and deconstruct an URL in a simple and easy manner.
    Path is a list of path elements.
    Query is a list of 2-uples (key, value).
    User can either configure netloc as a whole or username, password, host, and port independently.
    String representation of Url instance is the URL string itself.
    """

    class Path(list):

        SEP = '/'   # necessary for splitting

        def __init__(self, x):
            if type(x) is str:
                parts = [x for (i, x)
                            in enumerate(x.split(Url.Path.SEP))
                            if x or not i]
            else:
                parts = x
            list.__init__(self, parts)

        def __str__(self):
            return Url.Path.SEP.join(self)

        @property
        def is_absolute(self):
            return len(self)>0 and self[0]==''

        @property
        def is_relative(self):
            return len(self)>0 and self[0]!=''

        def canonify(self):
            if len(self)>0 and self[0]=='':
                tmp = self[1:]
                init = self[:1]
            else:
                tmp = self
                init = []
            def _canon(a, b):
                if b in ('.', ''):
                    return a
                if b=='..':
                    return a[:-1]
                return a+[b]
            canon = init + reduce(_canon, tmp, [])
            self.__init__(canon)
            return self

    netloc_re = re.compile('(([^:@]+)(:([^@]+))?@)?([^:]+)(:([0-9]+))?')

    def __init__(self, string_url=None, scheme='http', netloc='', path=[],
                 params='', query=[], fragment='', username=None,
                 password=None, host=None, port=None):
        """Construct an instance from an URL string

        :param scheme: Scheme for this request. Default is HTTP
        :param netloc: Default is ''
        :param path: Default is an empty list
        :param params: Default is an empty string
        :param query: Default is an empty list
        :param fragment: Default is an empty string
        :param username: Default is None
        :param password: Default is None
        :param host: Default is an empty string
        :param port: Default is None

        If netloc is not empty, it takes precedence over (username, password, host, port). Only host is mandatory if netloc is not provided."""

        if string_url is not None:
            p = urlexplode(string_url)
            scheme, netloc, path, params, query, fragment = p
            self.username = p.username
            self.password = p.password
            self.host = p.hostname
            self.port = p.port
            query = queryexplode(query)
        elif netloc:
            self.netloc = netloc
        else:
            self.host = host
            self.port = port
            self.username = username
            self.password = password

        self.scheme = scheme
        self._path = Url.Path(path)
        self.query = query
        self.fragment = fragment
        self.params = params

    def __str__(self):
        "The URL in human-copypastable form."
        return urlimplode(self)

    def __iter__(self):
        "Behave as a tuple or more precisely as a urlparse.ParseResult"
        yield self.scheme
        yield self.netloc
        yield str(self.path)
        yield self.params
        yield queryimplode(self.query)
        yield self.fragment

    def _netloc_get(self):
        "Reconstruct netloc. Not to be called directly."
        ret = []
        if self.username is not None:
            ret.append(self.username)
            if self.password is not None:
                ret.append(':' + self.password)
            ret.append('@')
        ret.append(self.host or '')
        if self.port is not None:
            ret.append(':' + str(self.port))
        return ''.join(ret)

    def _netloc_set(self, netloc):
        "Deconstruct netloc. Not to be called directly."
        optional0, self.username, \
        optional1, self.password, \
        self.host, \
        optional2, self.port = self.netloc_re.match(netloc).groups()

    def _path_set(self, p):
        self._path = Url.Path(p)

    def __add__(self, u):
        "Join two URLs."
        return Url(urljoin(str(self), str(u)))

    def __eq__(self, u):
        return str(self) == str(u)

    __repr__ = __str__

    path = property(lambda s: s._path, _path_set)
    netloc = property(_netloc_get, _netloc_set)
    is_absolute = property(lambda s: bool(s.host))
    is_relative = property(lambda s: not bool(s.host))
    is_secure = property(lambda s: s.scheme.lower() == 'https')


#if __name__=='__main__':
#    # A REPL to generate the example output.
#    import sys
#    for k in open(sys.argv[1]).xreadlines():
#        k=k.strip()
#        if k:
#            print '>>>', k
#            if not k.startswith('#'):
#                k = 'e='+k
#                exec k
#                if e:
#                    print e
