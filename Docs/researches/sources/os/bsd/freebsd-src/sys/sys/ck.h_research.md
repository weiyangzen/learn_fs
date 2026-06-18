# File Research: sources/os/bsd/freebsd-src/sys/sys/ck.h

## Purpose
Provides a small compatibility shim for Concurrency Kit queue/epoch interfaces across kernel and non-kernel builds.

## Main Elements
- In `_KERNEL`, includes `<ck_queue.h>` and `<ck_epoch.h>`.
- Outside `_KERNEL`, includes `<sys/queue.h>` and maps `CK_STAILQ_*`, `CK_LIST_*`, and `CK_SLIST_*` names to standard BSD queue macros.

## Dependencies And Integration
Used by code that wants CK-style queue type names while still compiling in userland without kernel CK headers.

## Risk Notes
The userland aliases cover only type/head/entry macro names, not the full CK API. Kernel code depends on actual CK headers being available.
