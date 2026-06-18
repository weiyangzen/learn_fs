<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/samba/process_single.c -->
# sources/user-network-fs/samba/source4/samba/process_single.c

## Purpose

`process_single.c` implements the simplest process model, where one process handles all tasks and accepted connections without forking.

## Important APIs, Types, and Functions

`single_ops` supplies `model_init`, `accept_connection`, `new_task`, `terminate_task`, `terminate_connection`, and `set_title`. `single_accept_connection()` accepts a socket and invokes the service callback in the current process. `single_new_task()` creates a task with a monotonically increasing task id. `process_model_single_init()` registers the model.

## Control Flow

When a listener is readable, the model accepts the socket, steals it under service-private memory, and calls the supplied `new_conn()` callback with a server ID derived from the current PID and socket fd. Task startup calls the service's `new_task()` callback, then optional `post_fork()` and `before_loop()` hooks even though no fork occurred.

## State and Persistence Behavior

The only model-local persistent state is the static task id counter starting at `INT32_MAX`, avoiding collisions with fd-based IDs. All service and connection state remains inside the one event loop.

## Dependencies and Integration Points

It depends on socket helpers, cluster IDs, and `service_details` hooks. It is registered as the internal `process_model_single` module in `source4/samba/wscript_build`.

## Risks and Edge Cases

One busy or stuck connection can affect all services because there is no process isolation. `single_terminate_task()` logs but does not shut down the process. Accept failures sleep for one second to avoid spinning under resource pressure.

## Test Signals

Useful signals are startup under `--model=single`, multiple simultaneous connections sharing one PID, task id uniqueness, hook ordering, and temporary accept failure behavior without log flooding.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/samba/process_single.c -->
