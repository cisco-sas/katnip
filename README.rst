Katnip
======

What is Katnip?
---------------

Katnip is a repository of implementations and extensions for Kitty_.

While Kitty defines the base classes and syntax,
it contains no specific implementation for any of them.
So, for example, in order to send a payload over TCP,
you need to create some class that extends ``ServerTarget``
and is able to send data over TCP,
and so on.

Katnip contains such classes.
Currently, Katnip contains various implementations of:

- Controllers for servers and clients
- Monitors
- Targets
- Legos
- Templates

Want to know more?
------------------

Read the documentations at `Read The Docs <https://katnip.readthedocs.org>`_.

How to install
--------------

::

    git clone https://github.com/cisco-sas/katnip.git katnip
    cd katnip
    pip install -e .


Contribution FAQ
----------------

*Found a bug?*
   Open an issue.

*Have a fix?*
   Great! please submit a pull request.

*Want to share you implementation?*
   Thank You! Please submit a pull request.

|docs|


.. |docs| image:: https://readthedocs.org/projects/katnip/badge/?version=latest
    :alt: Documentation Status
    :scale: 100%
    :target: https://katnip.readthedocs.org/en/latest/?badge=latest

.. _Kitty: https://github.com/cisco-sas/kitty
