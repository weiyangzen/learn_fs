# File Research: sources/virtualization/nbd/configure.ac

Autoconf configuration script for the NBD package.

It initializes package metadata from `support/genver.sh`, enables Automake/libtool, and exposes feature toggles for large file support, syslog, debug mode, GnuTLS, libnl/netlink, and manpage generation.

It checks compiler/tooling requirements including C compiler, C preprocessor, lex, Bison from Autoconf Archive, pkg-config, endian, integer sizes, dirent type support, and functions such as `llseek`, `mkstemp`, `fdatasync`, `splice`, and `sync_file_range`.

Platform feature checks define support for `FALLOC_FL_PUNCH_HOLE`, `BLKDISCARD`, splice plus `F_SETPIPE_SZ`, Windows zero-data ioctl support, GLib/gthread, optional socket/nss wrapper tests, `g_memdup2`, and `_BSD_SOURCE` needs.

The script builds `nbd-client` only on Linux hosts, marks a TLS huge test as expected failure on Darwin, substitutes manpage config paths, links selected source files into test run directories, and configures Makefiles, generated manpage SGML, docs, tests, and systemd files.
