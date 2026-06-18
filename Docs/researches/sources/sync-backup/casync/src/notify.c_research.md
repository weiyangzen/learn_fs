# sources/sync-backup/casync/src/notify.c

Purpose: implements sd_notify-style readiness notification for helpers that need to tell a parent process they are ready.

Important APIs/types/functions: `send_notify(const char *text)` reads `$NOTIFY_SOCKET`, constructs an abstract or pathname UNIX datagram address, opens `AF_UNIX/SOCK_DGRAM|SOCK_CLOEXEC`, sends the text with `sendto`, and returns `1` on sent, `0` when no socket is configured, or negative errno.

Control flow/state: no persistent state beyond environment lookup. The leading `@` convention is translated to Linux abstract namespace by replacing it with a NUL byte in `sun_path`.

Dependencies/integration: used by services/tests coordinated by `notify-wait.c` and scripts that launch FUSE/NBD/HTTP helpers.

Risks/test signals: socket path length is bounded by `sockaddr_un`; too-long values return `-EINVAL`. Datagram send failures surface as negative errno. Readiness tests indirectly validate it via `notify-wait`.

Source research group: `subset-b-009122`.
