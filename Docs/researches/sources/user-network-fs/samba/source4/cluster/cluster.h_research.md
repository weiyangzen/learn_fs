# sources/user-network-fs/samba/source4/cluster/cluster.h

## Purpose
Public header for the source4 cluster abstraction. It defines equality macros for cluster-aware server identifiers, declares the message callback type, and exposes the public cluster wrapper APIs.

## Important APIs, types, and functions
- `cluster_id_equal(id_1, id_2)` compares `pid`, `task_id`, and `vnn`.
- `cluster_node_equal(id1, id2)` compares only `vnn`.
- `cluster_message_fn_t` is a callback taking `struct imessaging_context *` and `DATA_BLOB`.
- Public prototypes include `cluster_id()`, `cluster_db_tmp_open()`, `cluster_backend_handle()`, `cluster_message_init()`, and `cluster_message_send()`.

## Control flow
This header has no runtime control flow, but its macros are evaluated inline and may evaluate arguments more than once if callers pass expressions with side effects.

## State and persistence behavior
No state is stored in the header. The APIs it declares can create cluster-aware server IDs, open temporary databases, and send/register messages through the active backend.

## Dependencies and integration points
Includes generated `server_id.h` and forward-declares `imessaging_context`. It is the stable public include used by cluster consumers.

## Risks and edge cases
- Equality macros compare only selected fields; `unique_id` is intentionally not part of equality here, which matters when mixing source3/server-id semantics.
- Macros do not guard NULL pointers.

## Test signals
Tests should confirm intended equality semantics, especially non-cluster IDs with `NONCLUSTER_VNN` and caller expectations around `unique_id`.
