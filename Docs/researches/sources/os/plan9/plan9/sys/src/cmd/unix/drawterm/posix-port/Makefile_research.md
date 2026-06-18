# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-port/Makefile

Builds a portable POSIX `../libmachdep.a` from `getcallerpc`, `md5block`, and `sha1block`.

Notably omits `tas.$O`, so this port does not provide an architecture-specific atomic test-and-set in the listed machine-dependent archive.
