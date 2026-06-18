# File Research: sources/os/bsd/freebsd-src/sys/sys/eventhandler.h

## Purpose
Defines the kernel eventhandler framework, a typed callback-list mechanism for low-frequency kernel lifecycle and subsystem notifications.

## Main Interfaces
- `struct eventhandler_list`: named callback list with lock, dead count, run count, and ordered entries.
- Lock macros: `EHL_LOCK`, `EHL_UNLOCK`, `EHL_LOCK_ASSERT`.
- Invocation and registration macros:
  - `EVENTHANDLER_LIST_DEFINE`
  - `EVENTHANDLER_DIRECT_INVOKE`
  - `EVENTHANDLER_DEFINE`
  - `EVENTHANDLER_INVOKE`
  - `EVENTHANDLER_REGISTER`
  - `EVENTHANDLER_DEREGISTER`
  - `EVENTHANDLER_DEREGISTER_NOWAIT`
- Core APIs: `eventhandler_register`, `eventhandler_deregister`, `eventhandler_deregister_nowait`, `eventhandler_find_list`, `eventhandler_prune_list`, `eventhandler_create_list`.
- Optional VIMAGE registration path.
- Priority constants: `EVENTHANDLER_PRI_FIRST`, `ANY`, `LAST`.
- Standard event declarations for shutdown, power, low memory, mountroot, VFS mount/unmount, process/thread lifecycle, coredump progress, UMA zone changes, KLD load/unload, framebuffer registration, CAM probe veto, swap events, newbus device events, route address changes, and kernel environment changes.

## Dependencies And Integration
Uses `_eventhandler.h`, mutexes, KTR tracing, power types, queues, SYSINIT, and many forward-declared subsystem types. Direct list definition avoids global list lookup for hot-ish events.

## Risk Notes
Handlers run outside the event list lock during callback execution, with `el_runcount` preventing unsafe pruning. Deregistration and dead-entry pruning must preserve this run-count protocol.
