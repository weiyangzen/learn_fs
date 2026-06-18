<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/samba/service.h -->
# sources/user-network-fs/samba/source4/samba/service.h

## Purpose

`service.h` defines the service callback contract used by source4 task services and process models.

## Important APIs, Types, and Functions

`struct process_details` currently carries a worker `instances` counter, with `initial_process_details` initialized to zero. `struct service_details` exposes `inhibit_fork_on_accept`, `inhibit_pre_fork`, `task_init`, `post_fork`, and `before_loop`. It declares `samba_service_init()` and includes generated `service_proto.h`.

## Control Flow

The header describes hook ordering across `standard`, `single`, and `prefork` models. `task_init()` creates service state, `post_fork()` handles per-process worker initialization where applicable, and `before_loop()` registers final event or messaging handlers before the event loop.

## State and Persistence Behavior

The structure carries behavior and lifecycle policy rather than state. `process_details.instances` lets prefork workers know their instance number.

## Dependencies and Integration Points

It includes stream and task service headers and is consumed by service modules, process models, and task startup helpers.

## Risks and Edge Cases

Hook order differs by model, especially prefork master versus worker behavior. Services must not assume that the `task_server` pointer or event/messaging contexts are unchanged between hooks.

## Test Signals

Model-specific service tests should assert hook order, `instances` values, and behavior when `inhibit_fork_on_accept` or `inhibit_pre_fork` is set.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/samba/service.h -->
