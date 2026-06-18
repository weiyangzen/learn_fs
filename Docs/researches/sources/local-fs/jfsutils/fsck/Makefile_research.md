# File Research: sources/local-fs/jfsutils/fsck/Makefile

This is the configured Automake output for building the JFS userspace checker binary `jfs_fsck` from the `fsck` subdirectory. It is generated from `Makefile.in` by `configure`, with concrete host/build paths and tool substitutions already resolved for a `jfsutils` 1.1.15 build.

The file builds one `sbin_PROGRAMS` target, `jfs_fsck$(EXEEXT)`, from the fsck source set: block map, connectivity, directory tree, EA, inode map, inode, metadata, fileset, workspace, xtree, main checker, run control, message handling, and headers. It compiles with `-I$(top_srcdir)/include -I$(top_srcdir)/libfs`, links `../libfs/libfs.a`, and adds `-luuid`. The object list explicitly includes `dirindex.o`, `fsck_message.o`, `fsckbmap.o`, `fsckconn.o`, and `fsckdire.o`, tying this group’s C files into the checker executable.

Because it is generated after configuration, it embeds resolved toolchain and install settings such as `CC = gcc`, `CFLAGS = -g -O2`, `AM_CFLAGS = -Wall -Wstrict-prototypes -fno-strict-aliasing`, `prefix = /usr`, `sbindir = /sbin`, `mandir = ${datarootdir}/man`, `LN = /usr/bin/ln`, and absolute build/source directories under `/data2/jfsutils-1.1.15`. The resolved `host_alias` is `mipsel-buildroot-linux-uclibc-`, but the compiler value is still plain `gcc` in this configured snapshot.

The main build rule links `jfs_fsck` from all fsck objects plus `../libfs/libfs.a`. Dependency tracking includes `.deps/*.Po` files for each C translation unit. Standard Automake targets cover compilation, install, uninstall, dist, clean, distclean, maintainer-clean, tags, ctags, and manpage install.

The JFS-specific install hooks create hard links:
`/sbin/fsck.jfs` points to installed `/sbin/jfs_fsck`, and `man8/fsck.jfs.8` points to `jfs_fsck.8`. The uninstall hook removes those aliases. This is important operationally because system fsck dispatch typically invokes filesystem-specific helpers by the `fsck.<fstype>` name.

As a generated file, this is build infrastructure rather than checker logic. Its main maintenance concern is that it contains configured absolute paths and generated dependency behavior. Source changes should usually be made in `Makefile.am` or Autotools inputs, not directly here.
