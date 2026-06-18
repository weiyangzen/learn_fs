# File Research: sources/os/bsd/freebsd-src/sys/sys/rmlock.h

Read completely: 184 lines.

## Purpose
Declares read-mostly lock and sleepable read-mostly lock kernel APIs, wrappers, sysinit helpers, and assertions.

## Main Elements
- Includes mutex, sx, lock, and private `_rmlock` definitions.
- Defines `RM_NOWITNESS`, `RM_RECURSE`, `RM_SLEEPABLE`, `RM_NEW`, and `RM_DUPOK` init flags.
- Declares `rm_init`, `rm_init_flags`, `rm_destroy`, `rm_wowned`, sysinit, debug and non-debug read/write lock operations, runlock operations, and invariant assertions.
- Requires `LOCK_DEBUG` from `sys/lock.h` and maps public macros to debug or non-debug implementations.
- Provides `rm_sleep` wrapper against the lock object.
- Defines `RM_SYSINIT_FLAGS` and `RM_SYSINIT`.
- Defines assertion aliases mapping to generic lock assertion constants.
- Declares `rmslock` APIs for sleepable read-mostly locks and inline ownership/assertion helpers.

## Dependencies And Integration
Used by read-mostly synchronization consumers, WITNESS/lock debugging, lock objects, sleep, SYSINIT/SYSUNINIT, and the implementation in `kern_rmlock.c`.

## Risk Notes
Callers must provide per-read `rm_priotracker` storage and include lock headers in the correct order. Sleepable and non-sleepable variants have different behavior and must not be substituted casually.
