<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/mountd/mountd.c -->
# sources/user-network-fs/ksmbd-tools/mountd/mountd.c

## Purpose

Implements the `ksmbd.mountd` daemon entry point, manager/worker process model, config reload, share listing protocol, daemonization, and signal handling.

## Important APIs, Types, and Functions

Important functions are `mountd_main`, `manager_init`, `manager_init_wait`, `worker_init`, `worker_init_wait`, `worker_sa_sigaction`, `list_config`, and `__splice_pipe`.

## Control Flow

The CLI parses port, foreground/daemon mode, config path, password DB path, verbosity, and version/help. The manager optionally forks/daemonizes, parses lock/subauth, then repeatedly starts a worker. The worker loads config, initializes signal handlers, processes netlink IPC, reloads config on SIGHUP, and lists shares through a pipe/FIFO protocol on SIGUSR1.

## State and Persistence Behavior

Persistent/runtime state includes `global_conf.pid`, lock file from `cp_parse_lock`, runstatedir FIFO paths, syslog/stdout logging mode, loaded config/user/share state, and health flags controlling reload/list/stop.

## Dependencies and Integration Points

Depends on tools, config_parser, ipc, management/share, signals, fork/pipe/splice/fcntl, and the kernel IPC channel.

## Risks and Edge Cases

Signal forwarding between manager and worker is subtle. FIFO list output depends on SIGUSR1/SIGIO ordering. Worker restart only occurs for `-ECHILD`; other errors terminate. Daemon mode redirects stdio and reports readiness with SIGUSR1.

## Test Signals

Tests should cover foreground and daemon startup, lock handling, config reload, share listing through control, worker crash/restart behavior, and clean shutdown on SIGTERM.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/mountd/mountd.c -->
