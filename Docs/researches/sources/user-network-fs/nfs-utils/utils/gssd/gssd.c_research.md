<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/gssd.c -->
# sources/user-network-fs/nfs-utils/utils/gssd/gssd.c

## Purpose
This is the `rpc.gssd` daemon main loop. It watches `rpc_pipefs` for kernel RPC client directories, opens their `gssd` or legacy `krb5` upcall pipes, dispatches upcalls into worker threads, and manages daemon configuration, signals, and timeout watchdogs.

## APIs And Control Flow
`read_gss_conf` and option parsing set pipefs, keytab, ccache search paths, DNS behavior, gssproxy use, timeouts, and verbosity. `main` normalizes `$HOME`, optionally enables `GSS_USE_PROXY`, builds the ccache search list, initializes logging, daemonizes, checks GSS mechanisms, creates a libevent base, opens pipefs, initializes inotify, registers SIGHUP rescans and pipefs events, starts the watchdog, scans current clients, and enters `event_base_dispatch`. Scanning builds `topdir` and `clnt_info` lists, adds inotify watches, opens client pipes, registers read events, and parses `info` files for server/service/address data. Inotify callbacks incrementally rescan or destroy clients.

## State, Dependencies, And Integration
Major state includes pipefs directory/fd, inotify fd, event base, config globals, `topdir_list`, client reference counts, `active_thread_list`, and mutexes. It depends on libevent, inotify, rpc_pipefs layout, nfs.conf, Kerberos utilities, and upcall handlers in `gssd_proc.c`.

## Risks And Test Signals
Risks include complex lifetime coupling between events, client refs, and worker threads; reliance on `d_type`; DNS fallback behavior; watchdog cancellation safety; global per-process environment changes; and empty pipefs treated as fatal. Test pipefs create/delete/rescan paths, SIGHUP, malformed `info`, RDMA-to-TCP conversion, foreground/daemon modes, gssproxy env setup, timeout clamping, and shutdown cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/gssd.c -->
