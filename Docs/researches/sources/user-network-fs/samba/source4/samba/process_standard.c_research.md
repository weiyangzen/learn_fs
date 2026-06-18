<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/samba/process_standard.c -->
# sources/user-network-fs/samba/source4/samba/process_standard.c

## Purpose

`process_standard.c` implements a process model where each task runs in its own process and, unless inhibited, each accepted connection is handled by a forked worker process.

## Important APIs, Types, and Functions

`standard_ops` implements `model_ops`. `struct standard_child_state` tracks child PID and pipe fds for cleanup. `struct process_context` carries service name, parent-control fd, and fork-on-accept flags. Key functions are `setup_standard_child_pipe()`, `standard_child_pipe_handler()`, `standard_accept_connection()`, `standard_new_task()`, `standard_pipe_handler()`, `standard_terminate_connection()`, and signal handlers.

## Control Flow

Task startup forks a child, reinitializes tevent, LDB, and messaging, registers parent-pipe and signal handlers, then runs the task callback and hooks. Connection accept first accepts the socket; if `inhibit_fork_on_accept` is set, the task process handles it directly. Otherwise, the parent creates a child tracking pipe and forks. The connection child frees listener state, reinitializes process-local subsystems, sets a connection title, invokes `new_conn()`, and runs its event loop until termination.

## State and Persistence Behavior

Parent process state tracks live children through pipes, avoiding zombies via `waitpid()`. `connections_active` and `smbd_max_processes` enforce max process limits. Per-child state is reset after fork; service databases are not persisted by this layer.

## Dependencies and Integration Points

The model integrates with tevent, messaging datagram cleanup, LDB fork hooks, socket addresses, cluster IDs, process titles, and loadparm `max smbd processes`.

## Risks and Edge Cases

Fork-after-accept has complex ownership: listener state must be released in children, and messaging/LDB must be reinitialized. If `SIGCHLD` is set to `SIG_IGN`, status collection can fail. `post_fork()` is not called per accepted connection, only after task init. Max-process counters rely on child-pipe cleanup.

## Test Signals

Tests should cover service task forking, per-connection forking, `inhibit_fork_on_accept`, max-process request dropping, child exit status logging, parent-pipe EOF shutdown, SIGTERM group termination, and cleanup without zombies.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/samba/process_standard.c -->
