# File Research: sources/os/bsd/netbsd-src/lib/libpam/staticmodules/Makefile

Read completely: 8 lines.

This makefile builds PAM modules statically by setting `MAKEDIRTARGETENV=MKPIC=no`, including `bsd.own.mk`, and delegating to `../modules` through `bsd.subdir.mk`.

Security/reliability notes: build-only file. It changes PIC behavior for the module subtree.
