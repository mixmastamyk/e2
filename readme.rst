
env
============

*Environment variables for sentient lifeforms.*

It's always been a tad clumsy to use environment variables and combine them
with other strings in Python,
compared to shell languages at least.
For example, look how easy in bash:

.. code:: shell

    ⏵ echo "Libraries: $PWD/lib"
    Libraries: /usr/local/lib

In Python-land however,
even the new-fangled string interpolation doesn't really help.
Required opposite/escaped quotes and brackets complicate and unfortunately
add to the visual clutter:

.. code:: python

    >>> from os import environ

    >>> print(f'Libraries: {environ["PWD"]}/lib')
    Libraries: /usr/local/lib

    >>> from os.path import join
    >>> join(environ['PWD'], 'lib')
    '/usr/local/lib'

Introducing the ``env`` module.
With it I've tried to whittle complexity down primarily via direct attribute
access:

.. code:: python

    >>> import env

    >>> print(f'Libraries: {env.PWD}/lib')
    Libraries: /usr/local/lib

    >>> join(env.PWD, 'lib')
    '/usr/local/lib'

But wait, there's more!

Install
---------------

.. code:: shell

    ⏵ pip3 install --user $PKG_NAME  # TBD

BSD licensed.


Options
-----------

By default the module loads the variables into its namespace,
so no additional mapping instance has to be created or imported.
Unless you want to configure the interface further, of course.
The following options are available to customize its behavior:

.. code:: python

    >>> from env import Environment

    >>> env = Environment(environ=os.environ,
                          blankify=False,
                          noneify=True,
                          readonly=True,
                          sensitive=…,
                        )

Note that a mapping of your own choosing can be passed as the first argument,
for testing or other purposes.

Noneify
~~~~~~~~~~~~

Enabled by default,
this one signals missing variables by returning None.
It allows one to easily test for a variable and not have to worry about
catching exceptions.
If the variable is not set,
None will be returned instead:

.. code:: python

    >>> if env.COLORTERM:
            pass


Blankify
~~~~~~~~~~~~

Off by default,
this option mimics the behavior of most command-line shells.
Namely if the variable isn't found,
it doesn't complain and replaces the variable with an empty string instead.
Could be a bug-magnet,
but here if you need it for compatibility.

Blankify takes precedence over Noneify if enabled.
If both ``blankify`` and ``noneify`` are disabled,
you'll get a lovely AttributeError or KeyError on missing keys,
depending on how the variable was accessed.

Aside—Get item (bracketed) form works also,
in cases where the variable name is in a string,
due to the fact that the module/Environment-instance is a dictionary underneath:

.. code:: python

    varname = 'COLORTERM'
    env[varname]


Readonly
~~~~~~~~~~~~

What it says on the tin.
By default the Environment does not allow modifications since such variables
are rarely read after start up.
This setting helps to remind us of that fact,
though the object can be changed to writable by disabling this option.


Sensitivity
~~~~~~~~~~~~~~~~~~~~~~

Variables are case-sensitive by default on Unix, not under Windows,
*sniff.* 😢

While sensitivity can be disabled to use variable names in lowercase,
be aware that variables and dictionary methods are in the same namespace,
which could potentially be problematic if they are not divided by case.
For this reason, using variable names such as "keys" and "items"
are not a good idea while in insensitive mode.
*shrug*


Entry Objects
----------------

While using ``env`` at the interactive prompt,
you may be surprised that a variable entry is not a simple string but rather
a string-like object called an Entry.
This becomes most evident at the prompt because it prints a "representation"
form by default:

.. code:: python

    >>> env.PWD                             # repr
    Entry('PWD', '/usr/local')

No matter however,
as any operation that occurs renders the string value as normal:

.. code:: python

    >>> print(env.PWD)
    /usr/local

The reason behind this custom object is so that variables can offer additional
functionality, such as parsing or converting the value to another type,
which we'll explore below.

Remember the ``env`` module/Environment-instance works as a dictionary,
while entry values are strings,
so their full functionality is available:

.. code:: python

    >>> for key, value in env.items():
            print(key, value)

    # output…

    >>> env.USER.title()
    'Fred'

    >>> env.TERM.partition('-')  # safer split
    ('xterm', '-', '256color')

Parsing & Conversions
-----------------------

Another handy feature is convenient type conversion and parsing of values
from strings.
For example:

.. code:: python

    >>> env.PI.float
    3.1416

    >>> env.STATUS.int
    5150

    >>> env.DATA.from_json
    {'one': 1, 'two': 2, 'three': 3}


Booleans
~~~~~~~~~~

To interpret boolean-ish "``0 1 yes no true false``" string values
case insensitively:

.. code:: python

    >>> env.QT_ACCESSIBILITY
    Entry('QT_ACCESSIBILITY', '1')

    >>> env.QT_ACCESSIBILITY.bool
    True

    >>> env = Environment(readonly=False)
    >>> env.QT_ACCESSIBILITY = '0'

    >>> env.QT_ACCESSIBILITY.bool
    False

As always, standard tests or ``bool()`` on the entry can be done to check for
standard string "truthiness."


Paths
~~~~~~~~

To split path strings on ``os.pathsep``,
with optional conversion to ``pathlib.Path`` objects,
use one or more of the following:

.. code:: python

    >>> env.XDG_DATA_DIRS.list
    ['/usr/local/share', '/usr/share']

    >>> env.SSH_AUTH_SOCK.path
    Path('/run/user/1000/keyring/ssh')

    >>> env.XDG_DATA_DIRS.path_list
    [Path('/usr/local/share'), Path('/usr/share')]



Compatibility
---------------

*"What's the frequency Kenneth?"*

This ``env`` module/Environment-instance attempts compatibility with KR's
`env <https://github.com/kennethreitz/env>`_
package by implementing its ``prefix`` and ``map`` functions:

.. code:: python

    >>> env.prefix('XDG_')
    {'xdg_config_dirs': '/etc/xdg/xdg-mate:/etc/xdg', …}

    >>> env.map(username='USER')
    {'username': 'fred'}

The lowercase transform can be disabled by passing another false-like argument.


Tests
---------------

Can be run here:

.. code:: shell

    ⏵ python3 -m $PKG_NAME -v


Pricing
---------------

*"I'd buy THAT for a dollar!" :-D*
