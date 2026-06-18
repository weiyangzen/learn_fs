# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_eventhandler.c

## Purpose
Implements the kernel eventhandler registry: named lists of callback entries sorted by priority, with safe deregistration while lists are being invoked.

## Key Elements
- Global list of lists: `eventhandler_lists`.
- Global mutex: `eventhandler_mutex`.
- Per-list locks via `EHL_LOCK`.
- Registration: `eventhandler_register()`.
- VIMAGE registration: `vimage_eventhandler_register()` when enabled.
- Deregistration: `eventhandler_deregister()`, `eventhandler_deregister_nowait()`.
- Lookup/create: `eventhandler_find_list()`, `eventhandler_create_list()`.
- Cleanup: `eventhandler_prune_list()`.

## Behavior
The subsystem initializes at `SI_SUB_EVENTHANDLER`. Lists are created lazily by name, with a second lookup after allocation to avoid races. Handlers are inserted by increasing priority, preserving efficient tail insertion when priorities are equal.

If a handler or whole list is deregistered while the list is running, entries are not immediately freed. They are marked with `EHE_DEAD_PRIORITY` and counted in `el_deadcount`; pruning later removes and frees them. Blocking deregistration waits until dead entries are pruned, while the nowait variant returns after marking.

## Research Notes
This file manages list infrastructure only. Actual event invocation is macro-driven in eventhandler interfaces, which rely on the dead-entry/prune protocol implemented here.
