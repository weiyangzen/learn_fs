<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/include/worker.h -->
# sources/user-network-fs/ksmbd-tools/include/worker.h

## Purpose

Declares the worker IPC queue entry point for mountd.

## Important APIs, Types, and Functions

Exposes `wp_ipc_msg_push(struct ksmbd_ipc_msg *msg)`.

## Control Flow

ipc.c pushes kernel events into worker processing through this function; worker.c dispatches events to user, share, session, tree, RPC, and SPNEGO handlers.

## State and Persistence Behavior

Queued `ksmbd_ipc_msg` objects are heap-allocated and transfer ownership to the worker pipeline.

## Dependencies and Integration Points

Depends on ipc.h message structure and mountd worker implementation.

## Risks and Edge Cases

Ownership and queue backpressure are implicit here; callers must not free messages after push unless the implementation says so.

## Test Signals

Tests require event injection through ipc.c or worker unit tests for each IPC event type.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/include/worker.h -->
