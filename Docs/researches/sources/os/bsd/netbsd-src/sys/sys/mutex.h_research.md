# File Research: sources/os/bsd/netbsd-src/sys/sys/mutex.h

## Purpose
Defines NetBSD kernel mutex abstraction, including adaptive/spin mutex types, machine-dependent contract, and public kernel mutex APIs.

## Main API
- Types: `kmutex_type_t`, opaque `kmutex_t`.
- Mutex classes: `MUTEX_SPIN`, `MUTEX_ADAPTIVE`, `MUTEX_DEFAULT`, `MUTEX_DRIVER`, `MUTEX_NODEBUG`.
- Private implementation constants under `__MUTEX_PRIVATE`.
- Kernel functions: `_mutex_init`, `mutex_init`, `mutex_destroy`, `mutex_enter`, `mutex_exit`, `mutex_spin_enter`, `mutex_spin_exit`, `mutex_tryenter`, `mutex_owned`, `mutex_ownable`.
- Object mutex routines: `mutex_obj_init`, `mutex_obj_alloc`, `mutex_obj_hold`, `mutex_obj_free`, `mutex_obj_refcnt`, `mutex_obj_tryalloc`.

## Dependencies
Includes `machine/mutex.h` for architecture-specific layout and operations; kernel mode also includes interrupt-level definitions.

## Risks and Notes
This header is a contract between machine-independent and machine-dependent kernel code. Architectures must provide either simple mutex support or the full operation set. Spin mutexes interact with IPL state and per-CPU spin-lock counts, so misuse can break interrupt or scheduler invariants.
