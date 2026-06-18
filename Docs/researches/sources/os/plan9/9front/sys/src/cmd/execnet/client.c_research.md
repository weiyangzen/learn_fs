# File Research: sources/os/plan9/9front/sys/src/cmd/execnet/client.c

This file implements per-client state and I/O behavior for the `execnet` 9P service. Each client represents an executed command exposed as a network-like connection with `ctl` and `data`.

Key responsibilities:
- Allocates/reuses `Client` slots with `newclient`.
- Manages teardown, reference counts, process killing, queued request cleanup, and message cleanup with `closeclient` and `die`.
- Queues read/write 9P requests and read messages.
- Matches queued output messages to queued read requests.
- Runs reader and writer threads around the command pipe.
- Handles flushes for queued or current read/write/exec requests.
- Executes commands via `/bin/rc -c "exec <cmd>"`.
- Parses control writes for `connect` and `hangup`.

Important implementation notes:
- `Zmsg` marks EOF/no-more-data in the message queue.
- `connect` strips any suffix after `!`, then prepends `exec `.
- Writer wakeups use a buffered `writerkick` channel.
- Process setup uses a pipe, duping the command’s stdin/stdout onto the same fd.
