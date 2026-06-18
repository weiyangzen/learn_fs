# File Research: sources/os/plan9/plan9/sys/src/lib9p/thread.c

This file provides libthread-based serving wrappers for lib9p.

Key behavior:
- Defines `tforker`, which starts work with `procrfork` and a 32 KiB stack.
- `threadlistensrv` sets global `_forker` to `tforker` and delegates to `_listensrv`.
- `threadpostmountsrv` sets `_forker` to `tforker` and delegates to `_postmountsrv`.

Role:
- Selects libthread process creation for listen and postmount server helpers.
- Complements `rfork.c`, which uses raw `rfork`.
