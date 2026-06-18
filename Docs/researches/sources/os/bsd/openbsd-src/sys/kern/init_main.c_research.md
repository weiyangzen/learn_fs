# File Research: sources/os/bsd/openbsd-src/sys/kern/init_main.c

Main OpenBSD kernel startup path.

Key behavior:
- Initializes process 0, CPU/current process state, timeouts, console, locks, UVM, disk subsystem, tty subsystem, random source, mbufs, sockets, SRP/SMR, process tables, file descriptors, pipes, kqueues, futexes, credentials, scheduler, task queues, network interface trees, and routing.
- Configures devices and pseudo-devices.
- Initializes VFS with `vfsinit()` and later mounts root through `mountroot`.
- Sets proc0 and init process current directories to the root vnode.
- Starts clocks, optional SysV IPC, crypto, domains, profiling, per-CPU subsystems, exec subsystem, and scheduler.
- Forks process 1 but blocks its `exec` until root is mounted.
- Creates kernel threads: pagedaemon, reaper, cleaner, update/syncer, aiodoned, page zeroing thread, and SMR thread.
- Boots secondary CPUs when configured.
- `start_init()` builds a minimal user stack and tries `/sbin/init`, `/sbin/oinit`, then `/sbin/init.bak`.
- `check_console()` validates `/dev/console`.

Filesystem/OS relevance:
- Core boot lifecycle file.
- Contains root filesystem mount, root vnode acquisition, process CWD setup, VFS initialization, swap initialization, and syncer/cleaner thread startup.
