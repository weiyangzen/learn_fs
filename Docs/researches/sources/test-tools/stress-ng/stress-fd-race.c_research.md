# sources/test-tools/stress-ng/stress-fd-race.c

Purpose: implements `fd-race`, a Linux pthread stressor that races file descriptor open, transfer, use, and close paths by passing fds over UNIX-domain sockets while threads concurrently operate on nearby descriptor numbers.

Important APIs/types/functions: `stress_fd_race_filename_t` stores candidate filenames and open flags. `stress_fd_race_context` shares args, fd arrays, max fd limit, socket port, device ids, pthread barrier, and the currently opening fd. `stress_race_fd_send()` and `stress_race_fd_recv()` send and receive descriptors with `SCM_RIGHTS`. `stress_fd_race_close_fds()` closes by `close_range()` or several ordered/random loops. `stress_fd_race_current()` races `dup`, `fstat`, syncs, `lseek`, `fcntl`, `flock`, `ioctl(FIONREAD)`, poll, and select against descriptors around `current_fd`.

Control flow: the main stressor creates a temp file, optionally scans top-level `/dev` and `/proc`, reserves a per-instance local socket port, allocates the fd array, initializes a pthread barrier, and forks. The child runs `stress_race_fd_client()`, connecting to the server, receiving up to `max_fd` descriptors, spawning four pthreads that write to received regular files when safe, then closing the fd set. The parent runs `stress_race_fd_server()`, accepting clients, repeatedly opening files from the list, publishing each fd with `sendmsg`, and closing the set while helper threads race current descriptor numbers.

State and persistence behavior: creates a temporary directory and file, builds a malloced filename list, reserves a socket address, and allocates fd storage. The UNIX socket path and temp file are unlinked in cleanup. Runtime state is intentionally shared across threads through `current_fd` and the fd array to provoke races.

Dependencies and integration points: compiled only on Linux with pthread and pthread barriers. It uses stress-ng networking helpers for socket addresses and port reservation, signal handling, scheduler application, OOM adjustment, temp files, and close-range shims. Registered as `CLASS_OS`, `VERIFY_ALWAYS`.

Risks: it intentionally pushes fd limits and ancillary-data send limits; expected transient errors include `EAGAIN`, `EINTR`, `ECONNRESET`, `ENOMEM`, `ETOOMANYREFS`, and `EPIPE`. Running as root is capped to keep fd headroom. Optional `/dev` probing avoids `/dev/watchdog` and numbered tty-like devices, but device side effects remain an environment risk.

Test signals: exercise default, `--fd-race-dev`, and `--fd-race-proc`; check skip paths when socket bind or pthread barrier setup fails. Watch for leaked UNIX socket paths, failed descriptor passing, unexpected sendmsg errors, and stability under low fd limits and high instance counts.
