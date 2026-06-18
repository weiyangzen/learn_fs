# File Research: sources/virtualization/open-iscsi/usr/event_poll.c

Implements the main `iscsid` event loop and child-process reaping helpers.

Core behavior:
- Tracks child process count with `reap_count`.
- Tracks reload child PID and invokes a callback after it is reaped.
- Supports shutdown callbacks by storing child PIDs, sending `SIGTERM`, and waiting until they exit.
- `event_loop_exit` marks the loop for shutdown and optionally stores a management IPC task to acknowledge later.
- `event_loop` polls three fds: control device, management IPC socket, and a `signalfd` for `SIGALRM`.

Loop behavior:
- Masks `SIGALRM` and receives it via `signalfd`, integrating actor timers with `poll`.
- Calls `actor_poll()` before each blocking poll.
- Handles control device events via `ipc->ctldev_handle`.
- Dispatches management IPC through legacy or current handlers based on `ipc->auth_type`.
- Uses a 1-second poll timeout when child reaping is pending.
- Flushes sysfs cache after each iteration.
- On clean shutdown, sends `ISCSI_SUCCESS` for the stored shutdown management task.

The file binds actor scheduling, netlink/control events, management IPC, sysfs cache invalidation, and child lifecycle into one single-threaded daemon loop.
