iptables-dynamic
================
Dynamically save and restore iptables rules for some chain(s)

- `Description <#description>`_
- `Dependencies <#dependencies>`_
- `Installation <#installation>`_
- `Usage <#usage>`_
- `Credits <#credits>`_

Description
-----------
When there's an iptables service restart, all of the docker rules gets wiped out. This script was written to dynamically save and restore iptables rules pertaining to some chain(s) and make them persist.


Dependencies
------------

- ``iptables`` (Must have the commands ``iptables-save`` and ``iptables-restore`` commands available)

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


Credits
--------
The copyright owner is `Regents of the University of California <http://regents.universityofcalifornia.edu/>`_ and this script is published under a `BSD 3-Clause <https://github.com/aalireza/iptables-dynamic/blob/master/LICENSE>`_ license. 

Developed at `UCSB LSIT <http://www.lsit.ucsb.edu/>`_
