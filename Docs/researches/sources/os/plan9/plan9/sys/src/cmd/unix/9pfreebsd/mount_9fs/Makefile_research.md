# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/9pfreebsd/mount_9fs/Makefile

Read fully: 21 lines, 412 bytes. SHA-256 prefix: `a20b3d49e9eb2fc0`.

This BSD makefile builds the FreeBSD `mount_9fs` command.

It sets:
- `PROG=mount_9fs`
- sources `mount_9fs.c`, `getmntopts.c`, and `crypt.c`
- man page `mount_9fs.8`
- debug-oriented `CFLAGS = -ggdb -O0`
- include path and `-DNFS` from `/usr/src/sbin/mount`
- optional Kerberos libraries when present and enabled
- standard `.include <bsd.prog.mk>`

Risk notes: despite the target name, it depends heavily on FreeBSD NFS mount support files and conditionals.
