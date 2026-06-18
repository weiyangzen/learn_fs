# File Research: sources/os/bsd/freebsd-src/sys/kern/uipc_domain.c

## Summary
Manages the global protocol domain list and protocol switch registration for FreeBSD networking. It also installs default protocol operation handlers for unsupported or generic operations.

## Main Responsibilities
- Provides default `EOPNOTSUPP` or `ENOPROTOOPT` protocol methods.
- Initializes `struct protosw` entries with generic socket operations and not-supported stubs.
- Adds and removes protocol domains.
- Finds domains and protocols by address family, socket type, and protocol number.
- Dynamically registers and unregisters protocol switch entries inside an existing domain.

## Key APIs
- `domain_add()`, `domain_remove()`, `pffinddomain()`, `pffindproto()`.
- `protosw_register()`, `protosw_unregister()`.
- `pr_listen_notsupp()` is exported; other not-supported handlers are private.

## Important Behavior
`pr_init()` requires every protocol to provide `pr_attach`, assigns the owning domain, fills generic send/receive/poll/sockbuf/AIO/kqueue methods, and fills missing protocol operations with not-supported stubs.

`domain_add()` only runs in the default VNET, honors an optional `dom_probe`, initializes all non-NULL protocol slots, asserts unique domain families under `INVARIANTS`, and inserts the domain into the global list.

`domain_remove()` only removes domains marked `DOMF_UNLOADABLE`. `domainfinalize()` records that early domain initialization has completed via `domain_init_status`.

`pffindproto()` matches a protocol when type matches and either registered protocol or requested protocol is zero, or both protocol numbers match.

## State and Synchronization
The global `domains` list and dynamic protocol slot updates are protected by `dom_mtx`. Lookup helpers walk without taking `dom_mtx`, relying on domain/protosw lifetime rules and the fact that most domains are not unloadable.

## Risks
Protocol removal assumes the caller has already shut down sockets and released all protocol-owned references. Dynamic registration modifies `dom_protosw` slots in place, so consumers rely on strict lifetime discipline outside this file.
