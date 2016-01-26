Introduction
============

What is Katnip?
---------------

Katnip is a repository of implementations and extensions for Kitty (link TBD).

While Kitty defines the base classes and syntax,
it contains no specific implementation for any of them.
So, for example, in order to send a payload over TCP,
you need to create some class that extends ServerTarget
and is able to send data over TCP,
and so on.

Katnip contains such classes.
Currently, Katnip contains various implementations of:

- :doc:`Controllers </katnip.controllers>` for :doc:`servers </katnip.controllers.server>` and :doc:`clients </katnip.controllers.client>`
- :doc:`Monitors </katnip.monitors>`
- :doc:`Targets </katnip.targets>`
- :doc:`Legos </katnip.legos>`
- :doc:`Templates </katnip.templates>`

Contribution FAQ
----------------

*Found a bug?*
   Open an issue.

*Have a fix?*
   Great! please submit a pull request.

*Want to share you implementation?*
   Thank You! Please submit a pull request.
