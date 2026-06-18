<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/mountd/ipc.c -->
# sources/user-network-fs/ksmbd-tools/mountd/ipc.c

## Purpose

Implements mountd's generic-netlink IPC transport to the ksmbd kernel module.

## Important APIs, Types, and Functions

Important functions are `ipc_msg_alloc`, `ipc_msg_free`, `ipc_msg_send`, `ipc_process_event`, `ipc_init`, `ipc_destroy`, `ipc_ksmbd_starting_up`, `nlink_msg_cb`, and generic event handlers. It defines netlink policies and command handlers for all `KSMBD_EVENT_*` types.

## Control Flow

Initialization allocates a netlink socket, disables seq checks, installs callbacks, connects to NETLINK_GENERIC, increases receive buffer size, registers/resolves the ksmbd family, sends a startup event filled from `global_conf`, and marks health running. Event processing waits in select, receives messages, validates version, and pushes supported request payloads to the worker queue. Sending wraps `ksmbd_ipc_msg` payloads as netlink attributes whose type equals the event id.

## State and Persistence Behavior

State is the static netlink socket `sk`, registered family metadata, queued heap IPC messages, and kernel-visible startup configuration. Interface list payloads are copied into startup config and freed from global config after send.

## Dependencies and Integration Points

Depends on libnl/libnl-genl, kernel ABI structures, tools/global_conf, worker queue, config parser list freeing, user/share management handlers downstream.

## Risks and Edge Cases

ABI policy min lengths must match kernel structures. Startup aborts on initialization failure. The 16 KiB message cap and fixed payload sizing can reject large share/RPC payloads. Version mismatch skips messages.

## Test Signals

Tests require a matching kernel module for startup and event round trips, plus unit tests for allocation limits, startup payload interface packing, and unsupported event handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/mountd/ipc.c -->
