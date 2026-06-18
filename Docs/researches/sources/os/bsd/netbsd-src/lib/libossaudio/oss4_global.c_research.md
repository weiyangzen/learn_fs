# File Research: sources/os/bsd/netbsd-src/lib/libossaudio/oss4_global.c

Handles OSSv4 global metadata ioctls for song/name/label fields. NetBSD follows common FreeBSD/Solaris behavior by treating them as unsupported no-ops that return `EINVAL`.

All recognized and unrecognized commands in this dispatcher currently return `-1` with `errno = EINVAL`.
