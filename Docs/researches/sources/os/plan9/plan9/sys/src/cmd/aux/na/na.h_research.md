# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/na/na.h

This header declares patch metadata and a script fixup routine for the `na` auxiliary code.

Key behavior:
- Defines `struct na_patch` with longword offset and patch type.
- Declares `na_fixup`, which patches a script using physical addresses, a patch table, and an external-value callback.

Filesystem relevance:
- Indirect: small support header, no filesystem implementation logic.
