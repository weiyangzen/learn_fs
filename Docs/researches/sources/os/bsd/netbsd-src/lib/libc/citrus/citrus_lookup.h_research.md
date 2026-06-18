# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_lookup.h

Interface for Citrus lookup files.

Key behavior:
- Defines case-sensitive and case-ignore flags.
- Declares simple lookup, sequence open/rewind/next/keyed lookup/count/close.
- Provides `_citrus_lookup_alias`, which returns the original key if lookup fails.

This header abstracts text-vs-compiled lookup storage for callers.
