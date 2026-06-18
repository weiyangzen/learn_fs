# File Research: sources/os/bsd/openbsd-src/sbin/slaacd/control.c

This file implements the non-`SMALL` runtime control socket for `slaacd`.

Key APIs:
- `control_init()`: creates a nonblocking close-on-exec Unix-domain socket, unlinks any old path, binds with restrictive umask, and sets group-writable permissions.
- `control_listen()`: starts listening and registers libevent accept/timer events.
- `control_accept()`: accepts control clients, handles fd exhaustion by pausing accepts, initializes imsg buffers, and queues connections.
- `control_connbyfd()`, `control_connbypid()`: locate active control clients.
- `control_close()`: tears down imsg/event/socket state and resumes accept if it had been paused.
- `control_dispatch_imsg()`: reads/writes client imsgs and handles control requests.
- `control_imsg_relay()`: forwards replies back to the control client matching an imsg pid.

Behavior and integration:
- Uses `TAILQ` to track active control connections.
- Handles `IMSG_CTL_LOG_VERBOSE` by forwarding verbosity changes to main and engine processes and applying `log_setverbose()`.
- Handles `IMSG_CTL_SHOW_INTERFACE_INFO` and `IMSG_CTL_SEND_SOLICITATION` by recording the client pid and forwarding interface indexes to the engine.
- Uses frontend helper functions for cross-process imsg composition.

Risk notes:
- Client routing relies on `imsg` pid association; only one active request per pid maps cleanly.
- The accept pause/resume path is important under `EMFILE`/`ENFILE`.
- Entire implementation is excluded under `SMALL`, so callers must compile-conditionally match the API.
