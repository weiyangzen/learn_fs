# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/flashfs/aux.h

This header declares flashfs allocation helpers.

Key behavior:
- Declares `emalloc9p`, `erealloc9p`, and `estrdup9p`.
- Defines `DMDIR` as `CHDIR` for compatibility with older directory-mode naming.

Filesystem relevance:
- Supporting header for the flashfs user-level filesystem implementation.
