# sources/user-network-fs/samba/source3/librpc/idl/rpc_host.idl

## Purpose
`rpc_host.idl` defines internal messages exchanged between `samba-dcerpcd` and RPC helper daemons. It supports passing new client connections to helpers and reporting helper capacity/status back to the host.

## Important APIs, types, and functions
- `rpc_host_client` carries the requested binding, inherited named-pipe authentication info, and raw bind PDU already read by `samba-dcerpcd`.
- `rpc_worker_status` reports server index, worker index, number of association groups, and number of client connections.

## Control flow
The host daemon accepts/reads an RPC bind, packages `rpc_host_client`, and sends it with a file descriptor to a helper daemon. After handoff, helpers report `rpc_worker_status` because the host no longer owns the socket lifecycle.

## State and persistence behavior
The structures are transient messaging payloads, not durable state. `rpc_worker_status` is `NDR_NOALIGN`, which fixes message layout expectations for internal transport.

## Dependencies and integration points
Imports include named-pipe auth and DCERPC IDL. The generated `NDR_RPC_HOST` subsystem is used by source3 RPC daemon orchestration and worker process management.

## Risks and edge cases
Descriptor passing and raw bind packet ownership must stay synchronized with message decode. `worker_index` and association group notes mention only 16-bit effective support despite `uint32` fields, so overflow or indexing mismatches are risks. Auth info inherited from SMB must be trusted only from the local daemon boundary.

## Test signals
Test new-client handoff, bind PDU preservation, named-pipe auth propagation, worker status updates after client disconnects, max worker/index boundaries, and mixed helper service arrays.
