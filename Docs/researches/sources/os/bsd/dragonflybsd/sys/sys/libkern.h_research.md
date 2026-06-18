# File Research: sources/os/bsd/dragonflybsd/sys/sys/libkern.h

Kernel-only libc-like utility declarations and inline helpers. Provides BCD/hex conversion tables, min/max/abs variants for several integer types, random APIs, compare/search/sort/string routines, fnmatch, mem helpers, and compatibility aliases such as `strchr` to `index`.

Filesystem code commonly depends on these primitives for path/string handling, sorting, matching, randomization, checks, and safe kernel-side utility operations.
