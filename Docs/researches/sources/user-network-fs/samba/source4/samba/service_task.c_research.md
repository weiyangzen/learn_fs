<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/samba/service_task.c -->
# sources/user-network-fs/samba/source4/samba/service_task.c

## Purpose

`service_task.c` provides the task-service wrapper that creates `task_server` objects, initializes imessaging, calls service-specific task initialization, and delegates lifecycle operations to process models.

## Important APIs, Types, and Functions

`task_server_startup()` is the public startup entry. `task_server_callback()` is passed into process models and creates `struct task_server`. `task_server_terminate()` logs, optionally notifies the parent `samba` process via IRPC `SAMBA_TERMINATE`, cleans messaging, and calls `model_ops->terminate_task()`. `task_server_set_title()` delegates title changes to the process model.

## Control Flow

Service startup allocates `task_state` with `service_details` and `model_ops`, then calls `model_ops->new_task()`. The selected model invokes `task_server_callback()` in the appropriate process. The callback fills event/loadparm/server-id/model/process-context fields, initializes imessaging, and calls `task_init()`. Termination may synchronously send a fatal termination request to the parent and then lets the model exit or continue as appropriate.

## State and Persistence Behavior

Task state is in-memory and talloc-owned from the event context. Messaging endpoints are registered per task and cleaned up during termination. Fatal termination can cause parent process exit through `samba_terminate()`.

## Dependencies and Integration Points

It depends on process models, imessaging/IRPC, generated `ndr_irpc_c`, loadparm, and `service_details` callbacks.

## Risks and Edge Cases

If `imessaging_init()` fails, `task_server_terminate()` is called on a partially initialized task. If `task_init()` fails, the task is returned as `NULL` without explicit cleanup in this function. Fatal termination uses a nested event loop through synchronous IRPC.

## Test Signals

Tests should cover successful task initialization, imessaging failure, `task_init()` failure cleanup, fatal parent notification, nonfatal model termination, and title delegation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/samba/service_task.c -->
