# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cyclic_impl.h

Private cyclic subsystem implementation header. It documents the platform backend contract in detail and defines backend ops, cyclic subsystem initialization, per-CPU cyclic state, tracing/coverage support, omni-cyclic bookkeeping, xcall arguments, and heap helpers.

Key elements:
- Large design comment specifies backend-supplied operations and call contexts for configure, unconfigure, enable, disable, reprogram, soft interrupt generation, interrupt-level set/restore, cross-call, suspend, and resume.
- `cyc_backend_t` is the platform callback vector and backend argument storage.
- Declares `cyclic_init()` and `cyclic_mp_init()` for backend registration and multiprocessor initialization.
- Debug builds enable `CYCLIC_TRACE`.
- `cyc_state_t` tracks per-CPU cyclic state: online, offline, expanding, removing, and suspended.
- `cyclic_t` records expiration time, interval, handler, argument, pending count, binding flags, and execution level.
- Producer/consumer and soft-buffer structs queue pending cyclic indexes between hard and soft interrupt contexts.
- Trace and coverage structs store diagnostic records when enabled.
- `cyc_cpu_t` stores per-CPU heap, cyclic array, soft buffers, backend, semaphores/modify levels, pending reprogram state, and optional trace buffers.
- `cyc_omni_cpu_t` and `cyc_id_t` maintain omni-cyclic per-CPU instances and globally visible cyclic IDs protected by an rwlock.
- `cyc_xcallarg_t` packages cyclic add/remove/move state for cross-call execution on target CPUs.
- Defines default per-CPU allocation, passive level, wait modes, and binary-heap parent/child index macros.

Dependencies:
- Depends on `cyclic.h` public types and kernel rwlocks, semaphores, CPU structures, and high-resolution time.
- Backend implementations are architecture/platform-specific and must call back into `cyclic_fire()`/`cyclic_softint()` as required.

Research notes:
- The backend contract is strict about CPU affinity, interrupt level, blocking behavior, and exactly-once cross-call semantics; violations can corrupt cyclic state.
- Per-CPU cyclics are organized in a heap by expiration time, with pending handoff through fixed producer/consumer buffers for soft levels.
- Suspend/unconfigure paths assume cyclic subsystem suspension and disabled interrupts for safe CPU dynamic reconfiguration.
