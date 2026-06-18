# File Research: sources/os/bsd/netbsd-src/lib/libc/string/strmode.c

Implements `strmode(mode_t mode, char *p)` when the host lacks it. It formats file type and permission bits into the traditional 11-character mode string plus NUL: file type, rwx triplets with setuid/setgid/sticky handling, a trailing ACL placeholder space, and terminator.

It recognizes directories, character/block devices, regular files, symlinks, sockets, FIFOs, whiteouts, doors, and optional archive bits.
