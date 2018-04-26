
env
============

*Environment variables for sentient bipeds.*

Was tired of how clumsy it is to use environment variables and combine them with
strings in Python.
For example, in bash::


    ⏵ echo "Libraries: $PWD/lib"
    Libraries: /usr/local/lib

But in Python-land it is a PITA, 
even with string interpolation::

    >>> from os import environ

    >>> environ["PWD"] + '/lib'
    /usr/local/lib

    >>> print(f'Libraries: {environ["PWD"]}/lib')
    Libraries: /usr/local/lib

With ``env`` I've tried to whittle that down to be as quick as possible with
direct attribute access.
Very little syntax or typing is needed::

    >>> import env
    >>> from os.path import join

    >>> join(env.PWD, 'lib')
    '/usr/local/lib'

    >>> print(f'Libraries: {env.PWD}/lib')
    Libraries: /usr/local/lib


Options
-----------

By default the env module loads all the variables into its namespace,
so no instance has to be created.
Unless you want to configure the instance further::

    >>> import env  # ready to go! or Configen-Sie…

    >>> from env import Environment

    >>> env = Environment(environ=optional_test_dict,
                          blankify=False,
                          noneify=True,
                          readonly=True
                          sensitive=…,
                        )


Sensitive, *sniff* 😢
~~~~~~~~~~~~~~~~~~~~~~

Variables are case-sensitive by default on Unix.

While you can disable this to use variable names in lowercase, be aware it that
variables and dictionary methods are in the same namespace, which could
potentially be problematic if they are not separable.
For this reason, accessing variable names such as "KEYS/keys" and "ITEMS/items"
are not a good idea while in insensitive mode.


Blankify
~~~~~~~~~~~~

Off by default,
this option mimics the behavior of most command-line shells.
Namely if the variable isn't found,
it doesn't crash or complain and merely replaces the variable with an empty
string instead.
Might be a bug-magnet,
but here if you need it.

Noneify
~~~~~~~~~~~~

This is the default,
which allows one to test for a variable before using it,
and not have to worry about crashes.
If the variable is not set,
None will be returned:

    >>> if env.COLORTERM:
            color = True

Readonly
~~~~~~~~~~~~

What it says on the tin.

By default the Environment is not able to be modified since such variables are
not often read after start up.
This setting helps to remind us of that fact.
But that can be changed with this option.


Objects, Methods
~~~~~~~~~~~~~~~~~~

::

    >>> env.PWD                             # repr
    Entry('PWD', '/usr/local')

    # don't worry, all string operations return the value
    >>> str(env.PWD)
    '/usr/local/lib'

As you saw above the Environment returns Entry objects,
a subclass of string.
This is so they can offer additional functionality,
such as parsing the value,
or converting it to another type.

The Environment has the methods of a dictionary,
while values have all the string methods available::

    >>> for key, value in env.items():
            print(key, value)
        … …

    >>> env.USER.title()
    'Fred'

But wait, there's more!  See below.


Type Conversion
---------------------

Another handy feature is convenient type conversion and parsing of values::

    >>> env.PI.float
    3.1416

    >>> env.STATUS.int
    5150

    >>> env.QT_ACCESSIBILITY.bool       # 0/1/yes/no/true/false
    True

    >>> env.XDG_DATA_DIRS.list
    ['/usr/local/share', '/usr/share']

    >>> env.SSH_AUTH_SOCK.path                  # pathlib.Path
    Path('/run/user/1000/keyring/ssh')

    >>> env.XDG_DATA_DIRS.path_list
    [Path('/usr/local/share'), Path('/usr/share')]


Compatibility
---------------

With KR's env module::

    >>> env.prefix('XDG_').keys()
    ['xdg_config_dirs', 'xdg_current_desktop', …]

The lowercasing can be disabled.
