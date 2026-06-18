# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-amd64/Makefile

Builds `../libmachdep.a` for POSIX amd64 drawterm from `getcallerpc`, portable C `md5block`, portable C `sha1block`, and `tas`.

Unlike i386, this Makefile has only a C compilation rule and does not generate assembly hash blocks.
