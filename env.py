#!/usr/bin/env python3
'''
    env.py

    Simplified access to environment variables.

    @copyright: 2018 by Mike Miller <mgmiller@studioxps>
    @license: BSD

'''
import os

__version__ = '0.50'
if os.name == 'nt':
    sensitive = False
else:
    sensitive = True


class Entry(str):
    ''' Represents an entry in the environment.

        Contains the functionality of strings as well as a few convenience
        functions.
    '''
    def __new__(cls, name, value):
        return super().__new__(cls, value)

    def __init__(self, name, value):
        self.name = name
        self.value = value

    #~ @property
    #~ def is_set(self):
        #~ ''' function_doc '''
        #~ if self: #.value:
            #~ return True

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

    @property
    def as_path(self):
        ''' Return a Path. '''
        from pathlib import Path
        return Path(self)

    @property
    def as_path_list(self, sep=os.pathsep):
        ''' Return list of Path objects.
        '''
        from pathlib import Path
        return [ Path(pathstr) for pathstr in self.split(sep) ]

    @property
    def from_json(self):
        ''' Parse a JSON string. '''
        from json import loads
        return loads(self)

    def __repr__(self):
        if self.value:
            return '%s=%s' % (self.name, self.value)
        else:
            return ''


class Environment:
    ''' Presents a simplified view of the OS Environment.

        blankify takes precedence.
    '''
    def __init__(self, environ=os.environ,
                       sensitive=sensitive,
                       noneify=True,
                       blankify=False,
                ):
        # setobj - prevents infinite recursion due to custom setattr
        # https://stackoverflow.com/a/16237698/450917
        setobj = object.__setattr__
        setobj(self, '_blankify', blankify)
        setobj(self, '_noneify', noneify),
        setobj(self, '_original_env', environ),
        setobj(self, '_sensitive', sensitive),

        if sensitive:
            setobj(self, '_envars', { name: Entry(name, value)
                                for name, value in environ.items() })
        else:
            setobj(self, '_envars', { name.lower(): Entry(name.lower(), value)
                                for name, value in environ.items() })

    def __contains__(self, name):
        return name in self._envars

    def __getattr__(self, name):
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
        self._envars[name] = value

        if self._original_env is os.environ:  # push to environment
            os.environ[name] = value

    def __delattr__(self, name):
        del self._envars[name]

    def prefix(self, prefix, lowercase=True):
        ''' Compat with kr/env, lowercased. '''         # str strips Entry

        return { (key.lower() if lowercase else key): str(self._envars[key])
                 for key in self._envars.keys()
                 if key.startswith(prefix)
               }

    def map(self, **kwargs):
        ''' Compat with kr/env. '''
        return { key: str(self._envars[kwargs[key]])    # str strips Entry
                 for key in kwargs
               }


if __name__ == '__main__':

    __doc__ += '''  # keep tests close

        Default::

            >>> env = Environment(variables)

            >>> env.USER                                # repr
            USER=fred

            >>> env.USER.title()                        # str ops
            'Fred'

            >>> env.user                                # missing --> None

            >>> print(f'term: {env.TERM}')              # interpolation
            term: xterm-256color

            >>> 'MISSING' in env                        # check existence
            False

            >>> 'EMPTY' in env                          # check existence
            True

            >>> bool(env.EMPTY)                         # check if empty
            False

            >>> env.PI.as_float
            3.14

            >>> env.STATUS.as_int
            5150

            >>> env.QT_ACCESSIBILITY.as_bool
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

        Unicode::

            >>> env.MÖTLEY = 'Crüe'
            >>> env.MÖTLEY
            MÖTLEY=Crüe

        Writing, not super useful but possible::

            >>> env.READY
            READY=no

            >>> env.READY = 'yes'

            >>> env.READY
            READY=yes

        Errors::

            >>> env.XDG_DATA_DIRZ.as_list               # TODO: figure out
            Traceback (most recent call last):
            AttributeError: 'NoneType' object has no attribute 'as_list'


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

    '''
    import sys, doctest

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
    env = Environment()
