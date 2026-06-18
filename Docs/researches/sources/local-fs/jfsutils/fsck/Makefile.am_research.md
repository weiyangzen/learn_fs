# File Research: sources/local-fs/jfsutils/fsck/Makefile.am

This is the concise Automake source for the JFS fsck build. It defines the include paths, link dependencies, installed binary, manpage, source list, and install aliases.

`INCLUDES` points at the project `include` and `libfs` directories. `LDADD` links the checker against `../libfs/libfs.a` and `libuuid`. The only installed program is `jfs_fsck`, and the installed manpage is `jfs_fsck.8`.

The `jfs_fsck_SOURCES` list is the authoritative module inventory for the checker: `fsckbmap.c`, `fsckconn.c`, `fsckdire.c`, `fsckdtre.c`, `fsckea.c`, `fsckimap.c`, `fsckino.c`, `fsckmeta.c`, `fsckpfs.c`, `dirindex.c`, `fsckwsp.c`, `fsckxtre.c`, `xchkdsk.c`, `fsckruns.c`, `fsck_message.c`, plus fsck headers. This group covers the build file and several core modules from that list.

The install hooks create filesystem-helper aliases with hard links: `jfs_fsck` is also installed as `fsck.jfs`, and `jfs_fsck.8` is also linked as `fsck.jfs.8`. The uninstall-local target removes those alias links.

This file is the right place to add or remove fsck translation units or change install behavior. The generated `Makefile.in` and configured `Makefile` mirror this file plus Automake boilerplate.
