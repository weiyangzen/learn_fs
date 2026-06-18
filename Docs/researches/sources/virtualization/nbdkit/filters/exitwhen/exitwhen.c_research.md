# File Research: sources/virtualization/nbdkit/filters/exitwhen/exitwhen.c

Purpose: shuts down nbdkit when configured external events occur and no clients are active.

Key details:
- Events include file created, file deleted, process exits, pipe/fd closed, and script exit status 88 where supported.
- Maintains event list, protected connection count, and `exiting` flag under a mutex.
- `dump_plugin` reports supported event types.
- Event checks use `access`, Linux `/proc/PID/stat` fd behavior or `kill(pid,0)`, `poll` for fd closure, and `system` for scripts.
- Background polling thread checks events every `exit-when-poll` seconds only when there are no active connections.
- `get_ready` exits cleanly before daemon startup if an exit condition already holds.
- `preconnect` rejects new connections once exiting.
- `.open` increments active connections; `.close` decrements and shuts down when exiting and count reaches zero.

Risk notes:
- Script mode runs shell commands with `system`; configuration must be trusted.
- Process-exit detection differs between Linux and non-Linux paths.
