<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/keyctl_watch.c -->
# sources/security-integrity/keyutils/keyctl_watch.c

## Purpose

`keyctl_watch.c` implements `keyctl` watch-queue subcommands for observing Linux key notifications. It can watch one key directly, add/remove watches to an inherited monitor, run a command in a watched session keyring, and synchronize pending notifications.

## Important APIs, Types, and Functions

The module uses `watch_queue.h` structures such as `watch_notification`, `key_notification`, `watch_notification_filter`, and notification subtype constants. `open_watch()` creates an `O_NOTIFICATION_PIPE` pipe and configures queue size/filter ioctls. `consumer()` polls/reads notification records, validates lengths, and dispatches to `saw_key_change()` or `saw_removal_notification()`. `parse_watch_filter()` converts one-letter subtype filters. Action functions are `act_keyctl_watch()`, `act_keyctl_watch_add()`, `act_keyctl_watch_rm()`, `act_keyctl_watch_session()`, and `act_keyctl_watch_sync()`.

## Control Flow

Direct watch mode parses optional filters, opens a watch queue, attaches watch ID 1 to the target key, and enters the consumer loop. Watch-session mode opens and optionally dup2s the watch fd, clears close-on-exec, forks a notification consumer, joins a new session keyring, watches it, exports `KEYCTL_WATCH_FD` to the child command, then waits for child/consumer termination and propagates status. Add/remove commands call `keyctl_watch_key()` with watch ID 2 or `-1`. Sync uses `PIPE_IOC_SYNC` when available or waits until `FIONREAD` reports no queued bytes.

## State and Persistence Behavior

State is process-local: global child PIDs, current session keyring ID, watch fd, debug flag, and notification filter. Persistent kernel changes are limited to watch registrations and a temporary/new session keyring. Log and GC files are appended by `watch_session`; direct watch writes to stdout.

## Dependencies and Integration Points

The module depends on Linux watch queues, notification pipes, `KEYCTL_WATCH_KEY`, `ioctl()` constants, `poll()`, `fork()/exec()`, and shared `keyctl` helpers. It integrates with command scripts through inherited fd `KEYCTL_WATCH_FD`.

## Risks and Edge Cases

Kernel support is required; unsupported notification pipes or watch ioctls fail at startup. The consumer exits on malformed or short records. `exit_cleanup()` kills child processes from the parent only, so PID bookkeeping must remain correct across forks. Filter parsing silently reserves one filter slot and only supports known key notification letters. Watch-session requires target fds 3..9.

## Test Signals

Relevant tests would assert event lines for instantiate/update/link/unlink/clear/revoke/invalidate/setattr, GC removal behavior, filter selection, inherited fd use, and sync fallback on kernels without `PIPE_IOC_SYNC`.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/keyctl_watch.c -->
