# File Research: sources/os/bsd/netbsd-src/sys/sys/queue.h

## Purpose
Provides BSD intrusive collection macros for singly linked lists, doubly linked lists, simple queues, tail queues, and singly linked tail queues.

## Main API
- SLIST: `SLIST_HEAD`, `SLIST_ENTRY`, accessors, foreach/safe foreach, init/insert/remove macros.
- LIST: `LIST_HEAD`, `LIST_ENTRY`, accessors, `LIST_MOVE`, init/insert/remove/replace macros.
- SIMPLEQ: `SIMPLEQ_HEAD`, `SIMPLEQ_ENTRY`, accessors, foreach/safe foreach, init/insert/remove/concat/last macros.
- TAILQ: `TAILQ_HEAD`, `TAILQ_ENTRY`, first/last/next/prev/foreach/reverse foreach, init/insert/remove/replace/concat macros.
- STAILQ: `STAILQ_HEAD`, `STAILQ_ENTRY`, accessors, init/insert/remove/foreach/concat/last macros.
- Optional debug support: `QUEUEDEBUG_*` checks under kernel `DIAGNOSTIC` or explicit `QUEUEDEBUG`.

## Dependencies
On NetBSD includes `sys/null.h`; debug mode uses `panic` in kernel or `err` in userland.

## Risks and Notes
These macros are intrusive and do not perform locking. Debug poisoning helps catch corrupted list links after removal. Some macros evaluate arguments more than once or rely on exact field names, so callers must use side-effect-free arguments.
