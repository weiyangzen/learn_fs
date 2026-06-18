# sources/user-network-fs/nfs-ganesha/src/tools/multilock/ml_posix_client.c

Purpose: `ml_posix_client.c` is the POSIX filesystem backend for multilock tests. It can be driven interactively, by a local script, or by `ml_console`, and it maps protocol commands to `open`, `read`, `write`, `lseek`, `close`, and `fcntl` lock operations.

Important APIs, types, and functions: `fno[MAXFPOS+1]` maps protocol file positions to OS file descriptors, and `lock_mode[]` records POSIX or OFD lock mode. `do_open()` validates OFD lock support with `F_OFD_GETLK` when requested. `do_lock()`, `do_unlock()`, `do_test()`, `do_hop()`, `do_unhop()`, and `do_list()` implement byte-range lock scenarios. `schedule_work()`, `cancel_work()`, `get_work()`, and `worker()` manage asynchronous/blocking `LOCKW` requests using pthreads and `glist`.

Control flow: `main()` initializes queue heads, starts worker threads, installs `SIGALRM`, `SIGPIPE`, and `SIGIO` handlers, parses modes, optionally connects to the console, then reads and dispatches one request per line. Nonblocking lock failure for `LOCKW` queues work and suppresses immediate response; completion is emitted by a worker. `QUIT` exits after responding.

State and persistence: state is process-local: file descriptors, per-fpos lock modes, alarm tag, worker queues, poll queue timing, and global parser I/O streams. File content and kernel locks are external state. Lock wait cancellation tracks queued ranges in `fno_work[]` and cancels work fully covered by an UNLOCK range.

Dependencies and integration points: it depends on POSIX file and lock APIs, OFD lock constants defined in `multilock.h` when absent, pthreads, signals, `gsh_list`, and the shared multilock parser. It is the primary backend for local filesystem lock test scripts.

Risks: `pthread_create()` return values are compared with `-1` even though pthreads return nonzero error numbers. `fno[0]` defaults to descriptor 0; most checks permit `fpos == 0`, so stdin can be used as an implicit fd unless scripts avoid it. `do_read()` converts bytes to C string length, which truncates at NUL. Blocking lock cancellation assumes `SIGIO` interrupts `fcntl(F_SETLKW)`. `get_work()` constructs `struct timespec` with fields reversed for `pthread_cond_timedwait()` (`tv_sec` receives delay but initializer order is `{ seconds, nanoseconds }` only if the implementation layout matches).

Test signals: sample scripts should cover POSIX and OFD modes, blocking lock grant/cancel/deadlock, lock splitting, hop/unhop, READ/WRITE/SEEK, alarm completion/cancel, client fork, and invalid fpos/fd paths.
