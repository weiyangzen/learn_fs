# File Research: sources/os/bsd/openbsd-src/sbin/unwind/control.c

Implements `unwind`’s local control socket server and imsg relay.

Socket setup:
- `control_init(path)` creates nonblocking close-on-exec Unix stream socket, unlinks stale socket path, binds with restricted umask, then chmods socket to user/group/other read-write.
- `control_listen(fd)` installs the accept event and a timer used to pause/resume accepting after fd exhaustion.

Connection management:
- `struct ctl_conn` stores a TAILQ entry and an `imsgev`.
- Connections are tracked by fd and by imsg pid.
- `control_accept()` accepts nonblocking clients, handles `ENFILE`/`EMFILE` by pausing accepts for one second, initializes imsg buffers, and registers read events.
- `control_close()` clears imsg buffers, removes events, closes fd, resumes accept if paused, and frees the connection.

Control dispatch:
- `control_dispatch_imsg()` reads/writes imsgs, verifies peer euid via `getpeereid()`, and requires root for reload/log-verbose requests.
- Handles:
  - `IMSG_CTL_RELOAD`: forwards to frontend/main path.
  - `IMSG_CTL_LOG_VERBOSE`: forwards to frontend and resolver, then updates local verbosity.
  - `IMSG_CTL_STATUS`, `IMSG_CTL_AUTOCONF`, `IMSG_CTL_MEM`: forwards to resolver.
- Invalid/unexpected messages are logged and ignored or close the connection depending on context.

Relay:
- `control_imsg_relay()` sends resolver/frontend responses back to the control client matched by pid.

Filesystem/storage relevance:
- No filesystem logic. Relevant as a reusable OpenBSD daemon control-plane pattern using Unix sockets, imsg, uid authorization, backpressure on fd exhaustion, and event-driven relay.
