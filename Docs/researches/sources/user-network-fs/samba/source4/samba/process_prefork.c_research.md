<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/samba/process_prefork.c -->
# sources/user-network-fs/samba/source4/samba/process_prefork.c

## Purpose

`process_prefork.c` implements the default source4 prefork process model: a top-level service master forks per-service prefork masters, which fork and supervise reusable worker processes.

## Important APIs, Types, and Functions

`prefork_ops` implements `model_ops`. Restart state is captured by `struct restart_context`, `master_restart_context`, and `worker_restart_context`. Key functions are `prefork_fork_master()`, `prefork_fork_worker()`, `prefork_child_pipe_handler()`, `prefork_restart()`, `prefork_restart_fn()`, `prefork_accept_connection()`, `prefork_new_task()`, `prefork_pipe_handler()`, `setup_handlers()`, and `prefork_reload_after_fork()`.

## Control Flow

`prefork_new_task()` forks a service master with `tfork`. The parent installs a child-pipe handler so unexpected master exit can be detected and restarted with backoff. The prefork master reinitializes tevent, LDB, and messaging after fork, creates the service task, registers an IRPC name, determines the configured child count, and forks workers. Workers listen on inherited sockets, run `post_fork()` and `before_loop()`, then process events. Worker exits are detected by `tfork_event_fd()` and restarted for fatal signals or nonzero status.

## State and Persistence Behavior

Runtime state lives in tevent contexts, control pipes, task servers, process titles, and imessaging registrations such as `prefork-master-*` and `prefork-worker-*`. No durable application data is written directly, but worker services may mutate Samba databases. Restart delay state is carried in memory and bounded by loadparm settings.

## Dependencies and Integration Points

The model integrates with `tfork`, tevent, messaging/IRPC cleanup, LDB fork hooks, cluster server IDs, loadparm parameters `prefork children`, `prefork backoff increment`, and `prefork maximum backoff`, plus `server_util` log-size tracing.

## Risks and Edge Cases

Fork/event-context separation is subtle: the master uses one event context for supervision and another to create worker-ready service state. Incorrect hook ordering can leave workers with stale messaging or DB handles. A child count of zero starts no workers. Fast-crashing workers can restart repeatedly until backoff limits. Control-pipe EOF is the shutdown signal.

## Test Signals

Tests should cover normal prefork startup, per-service child-count overrides, worker crash restart/backoff, master crash restart, parent-pipe shutdown, `inhibit_pre_fork`, SIGHUP log reopen, SIGTERM process-group cleanup, and IRPC process cleanup after worker death.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/samba/process_prefork.c -->
