# File Research: sources/virtualization/nbd/man/Makefile.am

Automake file for manpage generation.

It marks generated manpage artifacts as clean/distclean, distributes the `.sgml.in` source templates, and, when `MANPAGES` is enabled, builds and installs manpages for `nbd-server`, `nbd-client`, `nbd-trdump`, `nbd-trplay`, and `nbdtab` using `docbook2man`.
