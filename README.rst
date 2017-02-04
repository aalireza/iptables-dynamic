iptables-dynamic
================
Dynamically save and restore iptables rules for some chain(s)

- `What does it do? <#what-does-it-do>`_
- `Dependencies <#dependencies>`_
- `Installation <#installation>`_
- `Usage <#usage>`_
- `License <#license>`_

What does it do?
----------------
`iptables-dynamic` parses the output of `iptables-save` to dynamically save and restore rules for some chain(s).



Dependencies
------------

- ``iptables`` (Must have the commands ``iptables-save`` and ``iptables-restore`` commands available)
- At least, Python 2.7

Installation
-------------
::

  pip install iptables-dynamic


Usage
-----

::

  iptables-dynamic --chains DOCKER SOME-OTHER-CHAIN --save

which would save them at ``/etc/iptables/rules.v4``

One can restore those rules by

::

  iptables-dynamic --restore

One may also use ``ip6tables-dynamic`` for IPv6.


Use case example
++++++++++++++++

When there's an iptables service restart, all of the docker rules gets wiped out. The make the rules persist through
a service restart, you may edit your iptables' systemd unit files to call below at `ExecStopPre`: 

::

  iptables-dynamic --chains DOCKER --save

and call below at `ExecStartPost`:

::

  iptables-dynamic --restore



License
--------
The copyright owner is `Regents of the University of California <http://regents.universityofcalifornia.edu/>`_ and this script is published under a `BSD 3-Clause <LICENSE>`_ license. 

Developed at `UCSB LSIT <http://www.lsit.ucsb.edu/>`_
