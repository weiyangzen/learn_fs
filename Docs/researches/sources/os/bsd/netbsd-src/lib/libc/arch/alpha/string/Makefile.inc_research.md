# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/string/Makefile.inc

Alpha string build fragment.

Key behavior:
- Adds assembly implementations `bcopy.S`, `bzero.S`, and `ffs.S`.
- Adds `memcpy.S` and `memmove.S`.

Dependencies:
- Alpha architecture string/memory assembly sources.
