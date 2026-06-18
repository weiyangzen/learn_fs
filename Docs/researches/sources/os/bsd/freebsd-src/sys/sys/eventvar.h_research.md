# File Research: sources/os/bsd/freebsd-src/sys/sys/eventvar.h

## Purpose
Defines kernel-private `struct kqueue` internals.

## Main Interfaces
- Constants: `KQ_NEVENTS`, `KQEXTENT`.
- `struct kqueue` fields for:
  - lock and reference count
  - pending knote queue and count
  - select/sigio integration
  - owning file descriptor table
  - state bits
  - linear and hash knote tables
  - deferred task
  - credentials
  - fork source for copy-on-fork behavior
- State bits: `KQ_SEL`, `KQ_SLEEP`, `KQ_FLUXWAIT`, `KQ_ASYNC`, `KQ_CLOSING`, `KQ_TASKSCHED`, `KQ_TASKDRAIN`, `KQ_CPONFORK`.

## Dependencies And Integration
Kernel-only header. Depends on `_task.h` plus types declared by `event.h` and other kernel headers.

## Risk Notes
This structure is not user-serviceable but is central to kqueue synchronization. State-bit changes must match `kern_event.c`.
