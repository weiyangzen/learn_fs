# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/ctype_local.h

Read completely: 54 lines.

This header defines byte-oriented ctype cache sizes, compatibility classification bit masks, and declarations for the C locale ctype/toupper/tolower tables. Under `__BUILD_LEGACY`, it also declares legacy BSD ctype globals.

Important interactions: included by rune file/local headers and setlocale internals to connect wide/rune classification to traditional `ctype` table APIs.

Security/reliability notes: no executable logic. The fixed `_CTYPE_CACHE_SIZE` of 256 shapes cached rune and byte table behavior throughout the locale implementation.
