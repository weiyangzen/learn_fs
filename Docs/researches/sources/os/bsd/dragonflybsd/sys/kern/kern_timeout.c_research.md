# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_timeout.c

Implements DragonFlyBSD’s per-CPU callout facility using hashed timing wheels and per-CPU softclock helper threads.

Key structures:
- `struct wheel`: spinlock plus TAILQ of internal callouts.
- `struct softclock_pcpu`: per-CPU wheel array, running/next pointers, freelist, tick counters, and softclock thread.
- Public `struct callout` is backed lazily by an internal `struct _callout`.

Important flags:
- Frontend/backend state includes `CALLOUT_DID_INIT`, `CALLOUT_ACTIVE`, `CALLOUT_SET`, `CALLOUT_INPROG`, `CALLOUT_RESET`, `CALLOUT_STOP`, `CALLOUT_CANCEL`, `CALLOUT_AUTOLOCK`, `CALLOUT_MPSAFE`, `CALLOUT_PREVENTED`, and `CALLOUT_FREELIST`.

Important behavior:
- `swi_softclock_setup()` sizes the wheel per CPU, allocates per-CPU softclock state, initializes wheels, and creates one softclock thread per CPU.
- `hardclock_softtick()` advances per-CPU tick state from hardclock and schedules the softclock thread when due work exists or the CPU is behind.
- `softclock_handler()` walks wheel slots, validates callout ownership via verifier pointers, marks callouts in progress, handles MP lock compatibility, runs callbacks, processes queued reset/stop/cancel operations, and reclaims EXIS-safe internal callouts.
- `_callout_update_spinlocked()` is the central state machine for queued and unqueued callouts; it handles reset, stop, cancel, requeueing to safe future ticks, waiter wakeups, and prevented status.
- `_callout_gettoc()` lazily allocates and attaches an internal `_callout` under EXIS protection.
- `callout_reset()` schedules on current CPU; `callout_reset_bycpu()` schedules on a selected CPU.
- `callout_cancel()`, `callout_drain()`, `callout_stop_async()`, `callout_stop()`, `callout_deactivate()`, and `callout_terminate()` provide varying synchronous/asynchronous stop and teardown semantics.
- `_callout_setup_quick()` and `_callout_cancel_quick()` provide low-overhead internal callouts for `tsleep()`.
- `slotimer_callback()` runs every 10 seconds per CPU and calls `slab_cleanup()`.

Concurrency model:
- Wheel lists are protected by wheel spinlocks.
- Individual callout state is protected by `_callout.spin` plus atomic flag operations.
- EXIS is used to prevent freeing internal callout backing while other CPUs hold or inspect it.
- AUTOLOCK callouts use cancelable `lockmgr()` interlocks.

Filesystem relevance:
- Foundational delayed-work mechanism for kernel subsystems, including VFS/filesystem cache cleanup, delayed writes, timeouts, device timers, and watchdog-like retry paths.
