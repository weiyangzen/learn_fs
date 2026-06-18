# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/softint.c

Implements the kernel softcall mechanism used to run deferred callbacks at software interrupt priority.

Core model:
- A fixed pool of `NSOFTCALLS` entries backs a FIFO callback queue.
- Duplicate `(function, argument)` softcalls are coalesced.
- State is tracked with `SOFT_IDLE`, `SOFT_PEND`, `SOFT_DRAIN`, and `SOFT_STEAL`.
- `softcall_lock` protects the queue, free list, CPU-set state, and state machine.

Important paths:
- `softcall_init()` allocates the softcall pool and CPU set, initializes the spin mutex, sets initial state, and scales `softcall_delay` into clock ticks.
- `softcall()` enqueues a callback, triggers `siron()` when idle, and detects when the current draining CPU appears stuck.
- `softcall_choose_cpu()` selects another CPU to poke when the queue is not progressing, avoiding CPUs already poked, disabled CPUs, CPUs being offlined, and on x86 virtual CPUs not currently scheduled on a physical CPU.
- `softint()` drains the queue in FIFO order, releases the lock while executing callbacks, returns entries to the free list, and prevents multiple active drainers except during steal recovery.
- `kdi_softcall()` and the tail of `softint()` support kernel debugger deferred callbacks via `kdi_siron()`.

Reliability behavior:
- If higher-priority interrupt load prevents the soft interrupt from running, `SOFT_STEAL` allows another CPU to drain the queue.
- Poke frequency is rate monitored with `softcall_pokemax`; excessive poking increases `softcall_delay`.
- Quiesced or offline CPUs do not process the queue and are removed from the active CPU set.

Filesystem relevance:
- Deferred callback execution is broad kernel infrastructure. Filesystems and storage drivers can depend on soft interrupts for work that must be delayed out of high-level interrupt or scheduling contexts.
