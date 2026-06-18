# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/rsm/rsmka_path_int.h

## Role

`rsmka_path_int.h` defines internal RSM kernel-agent path-management structures for adapters, paths, IPC send queues, receive buffers, work queues, topology reporting, and reference-count macros.

## Path and Work Model

A single-thread/single-task deferred work model handles path-up/path-down processing. `work_token_t` and `work_queue_t` implement a simple FIFO with mutex and condition variable.

Path states include down, up, active, and going-down. Deferred opcodes cover IPC down/up.

`path_t` records remote node/device/hardware address, state, flags, lock, local adapter, sendq token, work tokens, receive buffer, incarnation numbers, reference count, and hold condition variable.

## Adapter and IPC Structures

`adapter_t` represents a local RSM controller with instance, devinfo, hardware address, RSMPI handle/attributes/ops, handler args, path list, and refcount.

`adapter_listhead_t` groups adapters by device name and tracks adapter/path counts.

`ipc_info_t` tracks per-remote-node liveness and sendq token lists.

`sendq_token_t` carries the RSMPI send queue handle, refcount, receiver buffer availability, and wait condition.

`recv_info_t` tracks received-message circular queue state, processed-message counts, remote sendq readiness, and receive taskq.

## Topology ABI

The topology structures describe local controllers and remote controller connections. `rsmka_topology_t` points to per-local-controller `rsmka_connections_t` records, each with remote controller entries and connection state. A 32-bit pointer variant is provided.

## Research Notes

This header is about cluster interconnect path state. The key invariants are reference-count macros, sendq token lifetime, path state transitions, incarnation numbers, and topology structure sizing/alignment.
