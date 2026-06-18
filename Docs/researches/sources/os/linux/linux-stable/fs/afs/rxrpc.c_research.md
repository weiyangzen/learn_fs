# File Research: sources/os/linux/linux-stable/fs/afs/rxrpc.c

## Scope

Maintains the RxRPC socket and call lifecycle used for outbound AFS/YFS RPCs and inbound cache-manager callback RPCs.

## APIs And Behavior

- `afs_open_socket()` creates and binds the callback socket for AFS and YFS callback services, configures security/managed responses, creates the RxGK CM key, installs RxRPC notifications, and precharges incoming calls.
- `afs_close_socket()` stops listening, flushes async work, drains outstanding calls, shuts down the socket, and releases keys.
- Call allocation/free helpers manage refs, work items, flat request/reply buffers, peer/server references, and deferred destruction.
- `afs_make_call()` begins an RxRPC call, sends fixed request data and optional write iter data, handles async extra refs, aborts on send failures, and records errors.
- `afs_deliver_to_call()` advances client/server call state, invokes type-specific unmarshalling, handles local/remote aborts, queues post-processing work, and marks completion.
- Incoming callback paths preallocate calls, attach RxRPC calls, decode operation IDs, route to cache-manager handlers, and send empty/simple replies.
- `afs_extract_data()` is the common receive helper that transitions call states when payloads complete.

## State And Dependencies

The file owns `afs_async_calls`, per-net socket state, incoming-call preallocation, `struct afs_call` state transitions, RxRPC peer/appdata, and socket notification callbacks. It depends on `net/af_rxrpc`, cache-manager routing, tracepoints, and call-type deliver/done/destructor hooks.

## Risks And Invariants

Call refs are split across synchronous waiters, async work, RxRPC notifications, and deferred free paths. Socket shutdown waits for `nr_outstanding_calls` to reach zero. Unmarshalling failures must abort with client/server marshal abort codes matching call direction.
