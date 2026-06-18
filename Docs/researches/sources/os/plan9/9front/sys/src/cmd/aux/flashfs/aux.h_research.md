# File Research: sources/os/plan9/9front/sys/src/cmd/aux/flashfs/aux.h

Role: Tiny compatibility header declaring flashfs allocation helpers.

Contents:
- Prototypes for `emalloc9p`, `erealloc9p`, and `estrdup9p`.
- Defines `DMDIR` as `CHDIR`, bridging older Plan 9 directory mode naming to newer code.

Use:
- Supports source files expecting lib9p-style helper names and `DMDIR`.
