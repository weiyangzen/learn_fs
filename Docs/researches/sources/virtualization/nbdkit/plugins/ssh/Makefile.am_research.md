# File Research: sources/virtualization/nbdkit/plugins/ssh/Makefile.am

Automake rules for `nbdkit-ssh-plugin.la`, gated by `HAVE_SSH`. It builds `ssh.c` with nbdkit/common include paths, warning flags, libssh CFLAGS/LIBS, utility library, Windows import hook, module/shared flags, and optional plugin linker script.

It distributes the SSH plugin POD and conditionally generates `nbdkit-ssh-plugin.1`, inserting the shared magic-parameter documentation into the manual.
