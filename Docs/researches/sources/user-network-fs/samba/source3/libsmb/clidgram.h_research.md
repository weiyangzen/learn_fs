# sources/user-network-fs/samba/source3/libsmb/clidgram.h

## Purpose

`clidgram.h` is the public header for the NetBIOS datagram GetDC client API implemented by `clidgram.c`. It exposes asynchronous and synchronous entry points for discovering a domain controller through NBT mailslot NetLogon traffic.

## Important APIs and Types

- `nbt_getdc_send()` creates a `tevent_req` for a GetDC request. Callers supply a memory context, tevent context, Samba messaging context, DC socket address, domain name, optional domain SID, account name/flags, and requested NT version.
- `nbt_getdc_recv()` completes the async request and can return the negotiated/returned NT version, DC name, and optional `struct netlogon_samlogon_response`.
- `nbt_getdc()` is the blocking wrapper with an explicit timeout in seconds.
- The header includes `../libcli/netlogon/netlogon.h` so callers see `struct netlogon_samlogon_response`.

## Control Flow and Integration

The header follows Samba's normal async pattern: `*_send()` starts work, a caller polls or chains callbacks on the `tevent_req`, and `*_recv()` transfers outputs. The synchronous helper wraps that flow for callers that are not already in an event loop. Consumers must link with the source3 libsmb datagram implementation and provide a valid `messaging_context`.

## State and Persistence Behavior

The header defines no storage. Ownership semantics are implied by the prototypes: returned strings and response structures are placed under the caller-provided `mem_ctx` in `nbt_getdc_recv()` or `nbt_getdc()`.

## Dependencies and Risks

The API surface hides that the implementation is IPv4-only and nmbd-dependent. Callers passing IPv6 addresses, missing messaging context, or expecting direct network I/O will receive implementation-level failures from `clidgram.c`. Because the optional output pointers can be `NULL`, callers should initialize their own variables and check `NTSTATUS` before using outputs.

## Test Signals

Compile-level tests should ensure the header is self-contained for users needing `struct netlogon_samlogon_response`. API tests should exercise async success, async failure, NULL optional outputs, and the synchronous timeout wrapper.
