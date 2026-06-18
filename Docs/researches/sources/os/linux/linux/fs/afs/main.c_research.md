# File Research: sources/os/linux/linux/fs/afs/main.c

## Purpose
Module and per-network-namespace initialization/cleanup for the Linux AFS client.

## Main Responsibilities
- Defines module metadata and parameters: `debug` and `rootcell`.
- Creates global workqueues for general AFS work, asynchronous calls, and lock management.
- Registers per-net namespace state and initializes per-net AFS structures.
- Initializes proc entries, cell database, RxRPC socket, filesystem registration, and `/proc/fs/afs` symlink.
- Tears down all global and per-net resources on namespace exit or module exit.

## Key Functions and Data
- `afs_net_init()` initializes `struct afs_net`, sysname defaults, procfs, cell DB, and RxRPC transport.
- `afs_net_exit()` marks the namespace dead and purges probes, cells, servers, sockets, procfs, sysnames, IDs, and address preferences.
- `afs_init()` allocates workqueues, registers pernet ops, registers the filesystem, and creates the proc symlink.
- `afs_exit()` removes procfs, unregisters filesystem/pernet ops, destroys workqueues, clears permit cache, and waits for RCU.
- `afs_init_sysname` is selected at compile time by architecture.

## Important Details
- Initialization runs as `late_initcall()` because the RxRPC socket requires networking to be available.
- `net->servers_outstanding` starts at `1`, supporting probe/server cleanup wait semantics.
- Error paths unwind in reverse order and mark `net->live = false` before teardown.
