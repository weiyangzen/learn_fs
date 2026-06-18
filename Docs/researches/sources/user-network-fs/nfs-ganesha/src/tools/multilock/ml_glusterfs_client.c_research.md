# sources/user-network-fs/nfs-ganesha/src/tools/multilock/ml_glusterfs_client.c

Purpose: `ml_glusterfs_client.c` is a multilock client backend using the GlusterFS libgfapi. It speaks the shared multilock text protocol but performs open/read/write/seek/lock operations through `glfs_*` handles instead of POSIX file descriptors.

Important APIs, types, and functions: `openserver()` connects to the console and sends `HELLO`. `do_open()` uses `glfs_h_lookupat()`, `glfs_h_creat()`, and `glfs_h_open()`; `do_write()`, `do_read()`, and `do_seek()` use `glfs_write()`, `glfs_read()`, and `glfs_lseek()`. Lock operations use `glfs_fd_set_lkowner()` and `glfs_posix_lock()`. The threaded blocking-lock infrastructure is built from `struct work_item`, `work_queue`, `poll_queue`, `fno_work[]`, `schedule_work()`, `cancel_work()`, `get_work()`, and `worker()`.

Control flow: `main()` initializes per-fpos queues, starts one poller plus four worker threads, installs signal handlers, parses console/script/GlusterFS options, initializes the Gluster volume with `glfs_new()`, `glfs_set_volfile_server()`, `glfs_set_logging()`, and `glfs_init()`, then reads protocol commands. Commands are parsed by `parse_request()` and dispatched to backend operations. Blocking `LOCKW` attempts first try nonblocking lock acquisition; if unavailable, the work item is queued and a later worker/poller response completes it.

State and persistence: process state includes console connection strings, `volname`, `glusterserver`, `fds[MAXFPOS+1]`, `handles[MAXFPOS+1]`, `lock_mode[]`, global `glfs_t *fs`, `alarmtag`, worker queues, and mutex/condition variables. No durable state is written by this tool; file content and locks live in the target Gluster volume. The code stores synthetic `r_fno = r_fpos` rather than an OS fd.

Dependencies and integration points: it depends on libgfapi headers (`glusterfs/api/glfs.h`, `glfs-handles.h`), pthreads, the local `gsh_list` intrusive list, POSIX signals, and the shared multilock parser. It integrates with `ml_console` and Gluster volume servers (`-g`, `-v`).

Risks: the `FORK` dispatcher checks `oflags == 7`, but full Gluster server mode sets bits through 31, so `FORK` may be rejected despite server mode. A stale comment and unused `ceph_mount_info *cmount` suggest copy/paste drift. `do_unhop()` does not set `lkowner` before each lock attempt, unlike other lock operations. Negative-return handling mixes `-rc` and `errno` conventions from gfapi. Worker cancellation relies on `pthread_kill(SIGIO)` interrupting lock waits, which may vary by libgfapi behavior.

Test signals: useful tests include Gluster volume initialization failures, create vs lookup open paths, POSIX-owner vs OFD-like owner behavior, LOCKW scheduling and cancellation through UNLOCK, hop/unhop range failure cleanup, script mode EOF, and server-mode `FORK` with all required Gluster options.
