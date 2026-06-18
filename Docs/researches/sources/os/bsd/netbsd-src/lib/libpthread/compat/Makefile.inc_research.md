# File Research: sources/os/bsd/netbsd-src/lib/libpthread/compat/Makefile.inc

## Purpose
Adds libpthread compatibility sources to the build.

## Main Responsibilities
- Sets `COMPAT` to the parsed directory.
- Adds compatibility directory to `.PATH.c`.
- Adds `compat_pthread_setname_np.c` to sources.
- Adds include path and suppresses nonliteral format warnings for that compatibility source.

## Dependencies
- Included by the broader libpthread build when compatibility support is desired.
