# File Research: sources/os/bsd/freebsd-src/sys/fs/cuse/cuse.c

Read completely: 2036 lines.

Purpose: implements FreeBSD CUSE, a userspace character-device framework. It exposes `/dev/cuse` as a server control device and lets privileged userland servers create character devices whose open/read/write/ioctl/poll/mmap operations are forwarded to that server.

Major structures:
- `struct cuse_server` tracks a server process, command queue, created devices, connected clients, allocated shared memory, refcount, lock/cv, and select/kqueue state.
- `struct cuse_server_dev` maps a userland `struct cuse_dev *` to a kernel `struct cdev`.
- `struct cuse_client` stores per-open state, command slots, buffers, flags, and the associated server/device.
- `struct cuse_client_command` represents in-flight open/close/read/write/ioctl/poll/signal/sync work with sx/cv synchronization.
- `struct cuse_memory` tracks mmap-able swap-backed VM objects by allocation number.

Server-side behavior:
- `/dev/cuse` open allocates a `cuse_server`, initializes queues, locks, and kqueue state, and inserts it into the global server list.
- Server ioctls fetch commands, synchronize completions, create/destroy devices, allocate/free device units, allocate/free shared memory, transfer data, query signals, set per-file handles, and wake pollers.
- Device creation uses `make_dev_credf()` after `PRIV_DRIVER` checks and sanitizes devnode names.
- Server close marks all clients/devices closing, wakes waiters, drains references, destroys devnodes, frees memory, and removes global state.

Client-side behavior:
- Client open rejects same-process server/client opens, creates per-client command slots, queues `CUSE_CMD_OPEN`, and waits for server completion.
- Read/write use `UIO_NOCOPY` and queue commands; small transfers use optimized kernel-side copy buffers, large transfers use process-to-process copying.
- Ioctl marshals fixed-size data through `ioctl_buffer` and exposes zero-length ioctl pointer values through `data_pointer`.
- Poll and kqueue route readiness through server commands and explicit wakeups.
- mmap maps server-allocated VM objects by allocation-number encoded offsets.

Concurrency/lifetime notes:
- Global server list uses `cuse_global_mtx`; per-server state uses `pcs->mtx`; per-command serialization uses `sx`.
- Command wait paths handle signals by queuing `CUSE_CMD_SIGNAL`.
- Process address-space copying uses `proc_rwmem()` with `PHOLD/PRELE`.
- Close/destruction paths are careful to wake blocked clients and avoid server self-destruction deadlocks.

Research notes:
- CUSE is a full bidirectional RPC layer between kernel cdev operations and userland.
- Error conversion maps negative `CUSE_ERR_*` protocol values to kernel `errno`.
- Static allocation limits are defined by `CUSE_BUFFER_MAX`, `CUSE_DEVICES_MAX`, and `CUSE_ALLOC_BYTES_MAX`.
