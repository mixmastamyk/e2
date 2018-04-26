#!/usr/bin/env python3
'''
    env.py

    Simplified access to environment variables.

    @copyright: 2018 by Mike Miller <mgmiller@studioxps>
    @license: BSD

'''
import sys, os
from collections.abc import MutableMapping

__version__ = '0.60'
if os.name == 'nt':
    sensitive = False
else:
    sensitive = True


class Entry(str):
    ''' Represents an entry in the environment.

        Contains the functionality of strings plus a number of convenience
        properties for type conversion.
    '''
    def __new__(cls, name, value):
        return super().__new__(cls, value)

    def __init__(self, name, value):
        self.name = name
        self.value = value

    @property
    def as_bool(self):
        ''' '''
        lower = self.lower()
        if lower.isdigit():
            return bool(int(lower))
        elif lower in ('yes', 'true'):
            return True
        elif lower in ('no', 'false'):
            return False
        elif self == '':
            return False
        else:
            return None

    @property
    def as_list(self, sep=os.pathsep):
        ''' Split a path string (defaults to os.pathsep) and return list.

            Use str.split instead when a custom delimiter is needed.
        '''
        return self.split(sep)

    @property
    def as_float(self):
        ''' Return a float. '''
        return float(self)

    @property
    def as_int(self):
        ''' Return a float. '''
        return int(self)
    int = as_int

    @property
    def as_path(self):
        ''' Return a Path. '''
        from pathlib import Path
        return Path(self)

    @property
    def as_path_list(self, sep=os.pathsep):
        ''' Return list of Path objects. '''
        from pathlib import Path
        return [ Path(pathstr) for pathstr in self.split(sep) ]

    @property
    def from_json(self):
        ''' Parse a JSON string. '''
        from json import loads
        return loads(self)

    def __repr__(self):
        if self.value:
            return "Entry('%s', '%s')" % (self.name, self.value)
        else:
            return ''


class Environment(MutableMapping):
    ''' Presents a simplified view of the OS Environment.

        blankify takes precedence over noneify.
    '''
    def __init__(self, environ=os.environ,
                       sensitive=sensitive,
                       blankify=False,
                       noneify=True,
                       readonly=True,
                ):
        # setobj - prevents infinite recursion due to custom setattr
        # https://stackoverflow.com/a/16237698/450917
        setobj = object.__setattr__
        setobj(self, '_blankify', blankify)
        setobj(self, '_noneify', noneify),
        setobj(self, '_original_env', environ),
        setobj(self, '_sensitive', sensitive),
        setobj(self, '_readonly', readonly),

        if sensitive:
            setobj(self, '_envars', environ)
        else:
            setobj(self, '_envars', { name.lower(): value
                                      for name, value in environ.items() })

    def __contains__(self, name):
        return name in self._envars

    def __getattr__(self, name):
        ''' Customize attribute access, allow direct access to variables. '''

        # need an loophole for configuring a new instance
        if name == 'Environment':
            return Environment

        if not self._sensitive:
            name = name.lower()

        try:
            return Entry(name, self._envars[name])
        except KeyError as err:
            if self._blankify:
                return self._envars.setdefault(name, Entry('', ''))
            elif self._noneify:
                return None
            else:
                raise AttributeError(name)

    def __setattr__(self, name, value):
        if self._readonly:
            raise AttributeError('Environment is read-only.')
        else:
            self._envars[name] = value

            if self._original_env is os.environ:  # push to environment
                os.environ[name] = value

    def __delattr__(self, name):
        del self._envars[name]

    # MutableMapping needs these implemented, defers to internal dict
    def __len__(self):                  return len(self._envars)
    def __delitem__(self, key):         del self._envars[key]
    def __getitem__(self, key):         return self._envars[key]
    def __setitem__(self, key, item):   self.data[key] = item
    def __iter__(self):                 return iter(self._envars)

    def __repr__(self):
        entry_list = ', '.join([ ('%s=%r' % (k, v)) for k, v in self.items() ])
        return 'dict(%s)' % entry_list

    def prefix(self, prefix, lowercase=True):
        ''' Compat with kr/env, lowercased.

        '''         # str strips Entry
        return { (key.lower() if lowercase else key): str(self._envars[key])
                 for key in self._envars.keys()
                 if key.startswith(prefix) }

    def map(self, **kwargs):
        ''' Compat with kr/env. '''
        return { key: str(self._envars[kwargs[key]])    # str strips Entry
                 for key in kwargs }


if __name__ == '__main__':

    __doc__ += '''  # keep tests close

        Default::

            >>> env = Environment(variables, readonly=False)

            >>> env.USER                                # repr
            Entry('USER', 'fred')

            >>> env.USER.title()                        # str ops available
            'Fred'

            >>> env.user                                # missing --> None

            >>> print(f'term: {env.TERM}')              # interpolation
            term: xterm-256color

            >>> 'NOPE' in env                           # check existence
            False

            >>> 'EMPTY' in env                          # check existence
            True

            >>> bool(env.EMPTY)                         # check if empty
            False

            >>> env['PI']                               # getitem
            '3.14'

            >>> env.PI.as_float                         # conversion
            3.14

            >>> env.STATUS.as_int
            5150

            >>> env.QT_ACCESSIBILITY.as_bool            # 0/1/yes/no/true/false
            True

            >>> sorted(env.JSON_DATA.from_json.keys())  # compat < 3.6
            ['one', 'three', 'two']

            >>> env.XDG_DATA_DIRS.as_list
            ['/usr/local/share', '/usr/share']

            # isinstance - avoid Windows errs
            >>> from pathlib import Path
            >>> isinstance(env.SSH_AUTH_SOCK.as_path, Path)
            True

            >>> all(map(lambda p: isinstance(p, Path), env.XDG_DATA_DIRS.as_path_list))
            True

            >>> sorted(env.prefix('XDG_', False).keys())
            ['XDG_DATA_DIRS', 'XDG_SESSION_ID', 'XDG_SESSION_TYPE']

            >>> env.map(username='USER')
            {'username': 'fred'}

        Writing is possible when readonly is set False (see above),
        though not usually useful::

            >>> env.READY
            Entry('READY', 'no')

            >>> env.READY = 'yes'

            >>> env.READY
            Entry('READY', 'yes')

        Unicode::

            >>> env.MÖTLEY = 'Crüe'
            >>> env.MÖTLEY
            Entry('MÖTLEY', 'Crüe')

        Noneify False::

            >>> env = Environment(variables, noneify=False)
            >>> env.USERZ                               # missing, kaboom!
            Traceback (most recent call last):
            AttributeError: USERZ

        Blankify True::

            >>> env = Environment(variables, blankify=True)
            >>> env.USERZ                               # missing --> blank
            <BLANKLINE>

        Sensitive False::

            >>> env = Environment(variables, sensitive=False)
            >>> str(env.USER)                           # repr
            'fred'
            >>> str(env.user)                           # repr
            'fred'

        Errors::

            >>> env.XDG_DATA_DIRZ.as_list               # TODO: figure out
            Traceback (most recent call last):
            AttributeError: 'NoneType' object has no attribute 'as_list'

    '''
    import doctest

    variables = dict(
        EMPTY='',
        JSON_DATA='{"one":1, "two":2, "three":3}',
        PI='3.14',
        READY='no',
        STATUS='5150',
        QT_ACCESSIBILITY='1',
        SSH_AUTH_SOCK='/run/user/1000/keyring/ssh',
        TERM='xterm-256color',
        USER='fred',
        XDG_DATA_DIRS='/usr/local/share:/usr/share',
        XDG_SESSION_ID='c1',
        XDG_SESSION_TYPE='x11',
    )
    doctest.testmod(verbose=(True if '-v' in sys.argv else False))

else:
    # Wrap module with instance for direct access
    #~ env = Environment()
    sys.modules[__name__] = Environment()
