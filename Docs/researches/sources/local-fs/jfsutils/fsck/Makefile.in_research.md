# File Research: sources/local-fs/jfsutils/fsck/Makefile.in

This is the Automake 1.11.1 template generated from `Makefile.am`. Unlike the configured `Makefile`, it preserves Autoconf substitution variables such as `@CC@`, `@CFLAGS@`, `@prefix@`, `@sbindir@`, `@AM_CFLAGS@`, `@MAINTAINER_MODE_TRUE@`, and dependency-tracking conditionals.

The template builds the same `jfs_fsck$(EXEEXT)` program from the same source/object set and links it with `$(LDADD)`, where `LDADD = ../libfs/libfs.a -luuid`. It installs the same `jfs_fsck.8` manpage and carries the same hard-link hooks for `fsck.jfs` and `fsck.jfs.8`.

Most of the file is standard Automake machinery: VPATH support, installation directory creation, program install/uninstall, dependency-file inclusion, `.c.o` and `.c.obj` compilation rules, manpage install, dist packaging, clean/distclean/maintainer-clean, tags/ctags, and recursive refresh hooks. The dependency includes are guarded with `@AMDEP_TRUE@` and fast dependency rules are guarded with `@am__fastdepCC_TRUE@`, so `configure` decides the concrete dependency behavior.

The template’s meaningful project-specific content is the same as `Makefile.am`: include paths, link libraries, the fsck source list, manpage distribution, and install aliases. Changes should normally originate in `Makefile.am`; regenerating this file requires the matching Automake version or compatible tooling.
