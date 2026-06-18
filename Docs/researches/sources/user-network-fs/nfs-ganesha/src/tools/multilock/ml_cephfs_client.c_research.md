# sources/user-network-fs/nfs-ganesha/src/tools/multilock/ml_cephfs_client.c

Purpose: CephFS backend client for the multilock test framework. It reads commands from stdin, a script, or a console server and performs CephFS low-level file I/O and lock operations.

Important APIs, types, and functions: command handlers include `do_open`, `do_close`, `do_lock`, `do_unlock`, `do_test`, `do_list`, `do_hop`, `do_unhop`, `do_seek`, `do_read`, `do_write`, `do_alarm`, and `do_fork`. Work management uses `struct work_item`, `schedule_work`, `cancel_work`, `get_work`, and worker threads. CephFS APIs include `ceph_create`, `ceph_conf_read_file`, `ceph_mount`, `ceph_mount_perms`, `ceph_ll_walk`, `ceph_ll_create`, `ceph_ll_open`, `ceph_ll_read`, `ceph_ll_write`, `ceph_ll_lseek`, `ceph_ll_setlk`, `ceph_ll_getlk`, `ceph_ll_close`, and `ceph_ll_put`.

Control flow: `main` initializes per-file work queues, starts one polling thread and four worker threads, installs signal handlers, parses mode/options, connects to a console if requested, mounts CephFS, then loops reading and parsing multilock commands. Most commands complete synchronously. Blocking lock commands can be scheduled to worker/poll queues and later responded to when granted, denied, canceled, or interrupted.

State and persistence: global arrays map framework file positions to CephFS `Inode *`, `Fh *`, and lock mode. Global `cmount` and `cephperms` hold CephFS mount state. Work queues and per-fno lists are protected by `work_mutex` and `work_cond`. Lock state persists in the CephFS cluster and MDS lock manager, not just this process.

Dependencies and integration points: integrates with `multilock.h` parsing/responding helpers, Ganesha list macros, POSIX sockets/signals/threads, and libcephfs. It can run interactively, script-driven, or as a named client connected to `ml_console`.

Risks: worker threads are started before CephFS mount setup; they block on empty queues but share globals after initialization. `pthread_create` checks `rc == -1`, but pthread APIs return nonzero error codes rather than `-1`. `pthread_cond_timedwait` uses a relative-looking `timespec` as an absolute timeout, which is likely wrong. Many globals are unsynchronized outside work queues, relying on command sequencing. `do_read` truncates binary data by writing NUL and then using `strlen`. Fork mode with active threads and CephFS mount state is risky. Shutdown does not join threads or unmount CephFS.

Test signals: multilock sample scripts can validate POSIX/OFD lock behavior, blocking locks, cancel/unlock interactions, lock listing, hop/unhop range operations, forked clients, and CephFS-specific low-level I/O paths.
