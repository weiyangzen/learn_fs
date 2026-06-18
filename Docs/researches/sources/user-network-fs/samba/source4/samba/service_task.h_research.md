<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/samba/service_task.h -->
# sources/user-network-fs/samba/source4/samba/service_task.h

## Purpose

This header defines `struct task_server`, the shared state object for source4 task-based services.

## Important APIs, Types, and Functions

`struct task_server` holds the tevent context, selected model ops, imessaging context, loadparm context, cluster/server ID, service private data, and process-model context.

## Control Flow

There is no runtime flow in the header. `service_task.c` initializes the structure and service modules consume it in `task_init`, `post_fork`, and `before_loop`.

## State and Persistence Behavior

The structure is in-memory per task process or task instance. `private_data` belongs to service implementations; `process_context` belongs to the selected process model.

## Dependencies and Integration Points

It includes generated `server_id` definitions and relies on forward declarations from including units for tevent, imessaging, loadparm, and model ops.

## Risks and Edge Cases

Ownership is implicit through talloc parentage. Services must not assume `msg_ctx` or `event_ctx` remain unchanged across hook phases, as documented in `service.h`.

## Test Signals

Compile and runtime service startup tests validate the structure contract. Hook-order tests should confirm fields are valid at `task_init`, `post_fork`, and `before_loop`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/samba/service_task.h -->
