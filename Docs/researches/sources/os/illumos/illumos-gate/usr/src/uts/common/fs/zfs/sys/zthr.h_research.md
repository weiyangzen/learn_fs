# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zthr.h

Declares the ZFS helper-thread abstraction.

Key elements:
- Opaque `zthr_t`.
- `zthr_func_t` is the worker callback signature.
- `zthr_checkfunc_t` decides whether work should run.
- Creation APIs support normal and timer-based helper threads.
- Declares destroy, wakeup, cancel, resume, and cancellation query.

Main dependencies and interactions:
- Used by background ZFS services that need a cancellable/resumable loop.
- The header relies on surrounding includes for `boolean_t` and `hrtime_t`.

Implementation notes:
- The API separates readiness checking from execution callback.
