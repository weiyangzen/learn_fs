# sources/user-network-fs/samba/source3/lib/addrchange.h

## Purpose
`addrchange.h` declares the public async API for Samba components that need notification when local network interface addresses are added or removed.

## Important APIs, Types, and Functions
- Opaque `struct addrchange_context`.
- `addrchange_context_create(TALLOC_CTX *mem_ctx, struct addrchange_context **pctx)`.
- `addrchange_send(TALLOC_CTX *mem_ctx, struct tevent_context *ev, struct addrchange_context *ctx)`.
- `enum addrchange_type` with `ADDRCHANGE_ADD` and `ADDRCHANGE_DEL`.
- `addrchange_recv(struct tevent_req *req, enum addrchange_type *type, struct sockaddr_storage *addr, uint32_t *if_index)`.

## Control Flow and State
The API uses Samba's standard tevent send/recv pattern. A daemon creates one context, starts a request with `addrchange_send`, receives one address-change event with `addrchange_recv`, then starts another request if it wants continuous monitoring. The context abstracts platform-specific watcher state.

## Persistence Behavior
No persistence. The API reports kernel/network state changes to in-memory daemon logic.

## Dependencies and Integration Points
It includes replacement/system network headers, talloc, tevent, and NTSTATUS. It is included by `addrchange.c`, smbd, winbindd, and torture tests.

## Risks
- Callers must handle `NT_STATUS_NOT_SUPPORTED` or NULL send requests on platforms without support.
- Continuous monitoring requires re-arming after every successful event.
- The output address and optional interface index are only valid after successful recv.

## Test Signals
Compile coverage in daemons, torture `run_addrchange`, platform stub tests, and daemon integration tests that verify listeners are re-armed after events.
