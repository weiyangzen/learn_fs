# File Research: sources/os/linux/linux/io_uring/register.c

Implementation of the `io_uring_register()` syscall dispatcher and several registration subfeatures. This file routes registration opcodes to resource, eventfd, buffer, SQPOLL, restriction, query, memory-region, resize, and BPF-filter helpers.

Key responsibilities:
- Implements operation probing through `IORING_REGISTER_PROBE`.
- Registers/unregisters personalities and stores credentials in `ctx->personalities`.
- Parses and installs ring restrictions and task-wide restrictions.
- Registers BPF filters for ring or task restrictions.
- Enables disabled rings and establishes the single issuer.
- Registers io-wq CPU affinity and max-worker limits.
- Implements ring resize for deferred-taskrun rings.
- Registers parameter memory regions and optional wait-argument storage.
- Dispatches all ring-bound registration opcodes through `__io_uring_register()`.
- Supports blind registration opcodes for query, restrictions, BPF filters, and msg-ring send without a ring fd.

Important data flows:
- `SYSCALL_DEFINE4(io_uring_register)` strips the registered-ring bit, handles fd `-1` blind ops, obtains the ring file, locks `ctx->uring_lock`, dispatches, traces, and releases the file if needed.
- Restriction registration parses user restrictions into bitmaps, then sets internal restricted-op flags.
- io-wq max-worker registration updates ctx limits, applies them to the current/SQPOLL io-wq, then propagates to registered task contexts.
- Ring resize allocates new ring and SQE regions, optionally parks SQPOLL, swaps pointers under mmap and completion locks, copies pending SQ/CQ entries, updates masks and flags, publishes the new RCU rings pointer, and frees old regions after RCU synchronization.

Concurrency and locking:
- Most ring-bound registration runs under `ctx->uring_lock`.
- SQPOLL io-wq affinity and worker-limit operations may drop `uring_lock` to obey lock ordering.
- Ring resize holds `ctx->mmap_lock` and `ctx->completion_lock` for pointer swap and pending CQ/SQ copy, and uses RCU for `rings_rcu`.
- Enabling a single-issuer disabled ring stores `submitter_task` before clearing `IORING_SETUP_R_DISABLED`.

Notable risks:
- Ring resize must reject overflow if pending SQ/CQ entries do not fit the new sizes.
- Restrictions can be registered only once and only before a disabled ring is enabled.
- Blind operations deliberately bypass ring lookup, so each blind opcode must validate its own user arguments.
