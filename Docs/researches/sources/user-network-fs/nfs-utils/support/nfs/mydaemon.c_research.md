# sources/user-network-fs/nfs-utils/support/nfs/mydaemon.c

Purpose: daemonization helper that lets the parent exit only after the child reports readiness.

Important APIs: `daemon_init(bool fg)` and `daemon_ready()`.

Control flow: foreground mode returns immediately. Background mode creates a pipe, forks, and the parent blocks reading an integer status. The child starts a new session, changes to `/`, moves the readiness pipe to fd 3, redirects stdin/stdout/stderr to `/dev/null`, closes descriptors >=4, and later `daemon_ready()` writes status 0 to the pipe and closes it.

State and persistence: process-global `pipefds[2]` tracks readiness communication. No durable state.

Dependencies and integration: depends on `xlog`, `closeall()`, syslog, fork/session/file descriptor APIs. Used by daemons that want reliable init scripts/system callers to see startup failure.

Risks: parent treats short read as failure, so a child that never calls `daemon_ready()` causes parent failure even if the daemon runs. Error paths call `exit()` directly. Descriptor juggling assumes fd 3 is available after `dup2()`.

Test signals: foreground no-op, successful parent wait, child setup failures, missing `daemon_ready()`, pipe write failure, and descriptor table cleanup.
