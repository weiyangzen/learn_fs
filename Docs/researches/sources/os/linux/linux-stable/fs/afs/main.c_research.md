# File Research: sources/os/linux/linux-stable/fs/afs/main.c

## Summary
Module and per-network-namespace initialization for the AFS client filesystem. It creates workqueues, registers pernet state, initializes cells/proc/rxrpc transport, registers the filesystem, and tears everything down on module exit.

## Main Responsibilities
- Defines module metadata and parameters.
- Selects the initial `@sys` substitution string by architecture.
- Initializes `struct afs_net` for each network namespace.
- Creates global AFS workqueues.
- Registers pernet operations and filesystem type.
- Creates `/proc/fs/afs` symlink to per-net proc state.
- Cleans up workqueues, permits, proc entries, cells, servers, and sockets.

## Key APIs
- Module init: `afs_init()` via `late_initcall`.
- Module exit: `afs_exit()`.
- Pernet callbacks: `afs_net_init()` and `afs_net_exit()`.
- Globals: `afs_wq`, `afs_debug`, `afs_init_sysname`.

## Important Behavior
`afs_net_init()` initializes socket/work state, cell trees, dynamic-root IDR, probe queues, server outstanding count, sysname list, proc entries, cell database, and rxrpc socket in order. Error paths unwind partial initialization and mark the namespace non-live.

`afs_init()` allocates three workqueues: general AFS work, async call processing, and lock management. It then registers pernet state, filesystem support, and the proc symlink.

## State and Synchronization
`net->live` gates probe scheduling and namespace activity during teardown. `servers_outstanding` starts at 1 and is used with probe/server cleanup waits. `afs_exit()` performs an `rcu_barrier()` after destroying workqueues and cleaning permit caches.

## Risks
Initialization ordering matters: rxrpc socket creation depends on networking being ready, hence `late_initcall`. Error paths must mirror successful setup to avoid leaked workqueues, proc entries, net state, or IDR contents.
