# File Research: sources/os/linux/linux/fs/afs/rxrpc.c

## Scope

This file maintains the AFS RxRPC socket, manages outgoing and incoming RxRPC calls, drives asynchronous call processing, sends cache-manager replies, and provides receive/extract helpers for RPC unmarshalling.

## Public And Internal APIs Covered

- Socket lifecycle: `afs_open_socket()` and `afs_close_socket()`.
- Call allocation/lifetime: `afs_alloc_flat_call()`, `afs_flat_call_destructor()`, `afs_put_call()`, `afs_deferred_put_call()`.
- Outgoing calls: `afs_make_call()` and `afs_wait_for_call_to_complete()`.
- Receive path: `afs_deliver_to_call()`, `afs_extract_data()`, `afs_protocol_error()`.
- Server-side replies: `afs_send_empty_reply()` and `afs_send_simple_reply()`.
- Incoming-call preallocation: `afs_charge_preallocation()` plus RxRPC callbacks for new/discarded/attached calls and OOB notification.

## Control Flow And Behavior

- `afs_open_socket()` creates an AF_RXRPC kernel socket, sets minimum encryption security, enables managed responses, creates the RxGK cache-manager token key, binds AFS and YFS callback services, installs RxRPC callbacks, listens, and charges incoming-call preallocation.
- `afs_make_call()` computes total transmit length, begins an RxRPC call, sends the fixed request and optional write iterator, and handles async self-references and abort cleanup.
- `afs_deliver_to_call()` repeatedly invokes the call-type deliver function while data is pending, translates unmarshalling/protocol errors to RxRPC aborts, runs completion callbacks, and queues follow-up work.
- Synchronous waiters sleep on `call->waitq` and deliver pending data themselves; async calls are queued on `afs_async_calls`.
- Incoming calls are accepted from preallocated `afs_call` objects, associated with peers/servers, routed by the first operation ID, and then delivered by callback-manager handlers.
- `afs_extract_data()` wraps `rxrpc_kernel_recv_data()` and advances AFS client/server call states when a full packet stream has been received.

## State And Data Structures

- Global `afs_async_calls` workqueue handles async RxRPC attention.
- `struct afs_call` tracks call type, RxRPC call, peer, key, server/vlserver, request/reply buffers, state, waitqueue, errors, abort codes, service ID, write iterator, and async refs.
- `struct afs_net` stores the socket, outstanding-call counter, preallocated incoming call, and OOB work.

## Dependencies

- Kernel RxRPC API: socket creation, begin/send/recv/abort/shutdown calls, peer access, security query, notifications, and call life checks.
- AFS call-type deliver/work/done/destructor hooks declared elsewhere in the AFS subsystem.

## Risks And Invariants

- Async calls take an extra self-reference; error paths must cancel queued work and drop that reference exactly once.
- `nr_outstanding_calls` gates socket teardown and must reach zero before release.
- Receive-state transitions distinguish client replies from server requests/reply acknowledgements.
- Protocol unmarshalling errors abort with protocol-specific RxRPC abort codes so peer-side failures are diagnosable.
