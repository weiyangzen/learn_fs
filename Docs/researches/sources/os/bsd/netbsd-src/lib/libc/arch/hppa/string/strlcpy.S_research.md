# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/string/strlcpy.S

This HPPA `_strlcpy` routine, weakly aliased to `strlcpy`, copies bytes until the destination limit or source NUL, NUL-terminates when the destination has space, then continues scanning the source to return its length. The file is present but the HPPA string make fragment notes it is not enabled.
