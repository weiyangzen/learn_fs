# File Research: sources/os/bsd/openbsd-src/sbin/iked/proc.c

This is OpenIKED’s generic privilege-separated process framework. It creates child processes, builds an imsg/socketpair communication mesh, drops privileges, runs libevent loops, and provides helpers for sending messages among process roles.

Key responsibilities:
- Maps process titles to `enum privsep_procid` with `proc_getid`.
- Re-execs child process roles with `-P <process>` and `-I <instance>` arguments in `proc_exec`.
- Initializes parent and child process topology in `proc_init` and `proc_setup`.
- Creates parent-child socketpairs first, then distributes inter-child socketpairs by file descriptor passing in `proc_connect` and `proc_open`.
- Accepts received process file descriptors with `proc_accept`, initializes `imsgbuf`, enables fd passing, and registers events.
- Closes imsg buffers/events and waits for child exits in `proc_close` and `proc_kill`.
- Runs a child role in `proc_run`: optional control socket setup, chroot, privilege drop, libevent initialization, signal registration, parent pipe acceptance, and role callback invocation.
- Dispatches imsg events in `proc_dispatch`, handling generic messages for verbosity, process-fd transfer, and process-ready handshakes after role-specific callbacks have had first chance.
- Provides message helper APIs: `imsg_event_add`, `imsg_compose_event`, `imsg_composev_event`, `proc_compose`, `proc_compose_imsg`, `proc_composev`, `proc_composev_imsg`, `proc_forward_imsg`, `proc_ibuf`, `proc_iev`, and `proc_flush_imsg`.

Important data flow:
- The parent constructs all socketpairs, passes endpoints using `IMSG_CTL_PROCFD`, then sends `IMSG_CTL_PROCREADY`.
- Children acknowledge readiness to the parent; once all acknowledgements arrive, the parent invokes the supplied connected callback.
- `proc_range` lets callers target all instances of a process role by passing `-1`.

Security and correctness notes:
- Child processes chroot and drop to configured users/groups before entering the event loop.
- `imsgbuf_allow_fdpass` is explicitly enabled for channels that pass descriptors.
- Unexpected generic imsg types are fatal, making the IPC protocol closed by default.
- `proc_flush_imsg` is documented as breaking async I/O and is used carefully during startup fd distribution to avoid descriptor buildup.
