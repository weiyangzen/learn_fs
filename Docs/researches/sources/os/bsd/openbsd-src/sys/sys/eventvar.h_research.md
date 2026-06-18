# File Research: sources/os/bsd/openbsd-src/sys/sys/eventvar.h

This kernel header defines the internal `struct kqueue`.

Key definitions:
- Constants: `KQ_NEVENTS`, `KQEXTENT`.
- `struct kqueue` with queue mutex, pending event list/count, refcount, knotes for kqueue-on-kqueue, owning filedesc, registered knote arrays/hash, deferred task, and state flags.
- State flags: `KQ_SLEEP`, `KQ_DYING`, `KQ_TASK`.

Behavior and integration:
- Includes mutex, refcount, and task headers.
- Complements public and kernel-facing declarations in `event.h`.

Risk notes:
- Lock annotations distinguish immutable, global klist-lock, atomic, and kqueue-lock fields.
- `kq_fdp` ties kqueues to descriptor tables, so fd-table teardown must coordinate with kqueue lifecycle.
