# sources/user-network-fs/samba/source4/rpc_server/samr/dcesrv_samr.h

## Purpose

This header defines the private server-side state objects used by the SAMR RPC implementation. It gives `dcesrv_samr.c` and the SAMR password helpers a common model for distinguishing handle types and attaching SAM database, domain, account, access-mask, SID, DN, loadparm, role, and enumeration-cache state to DCE/RPC policy handles.

## Important APIs, Types, And Functions

`enum samr_handle` defines the handle discriminator values consumed by `dcesrv_handle_create()` and `DCESRV_PULL_HANDLE()`: connect, domain, user, group, and alias. `struct samr_connect_state` stores the caller-visible `ldb_context *sam_ctx` and requested access mask for `samr_Connect*`.

`struct samr_guid_cache` stores a paged enumeration cursor: a `handle` field used as caller-specific cache metadata, an entry count, and a talloc-owned array of `struct GUID`. `enum samr_guid_cache_id` allocates cache slots for display info, domain group enumeration, and domain user/group operations. `struct samr_domain_state` ties a domain handle back to its connect state and SAM context, records the domain SID/name/DN, server role, BUILTIN flag, loadparm context, GUID caches, and the cached `samr_SamEntry` array used by user enumeration. `struct samr_account_state` attaches a user/group/alias account handle to its parent domain, SAM context, requested access mask, account SID/name, and account DN.

## Control Flow

The header itself has no executable control flow. Its structures define the lifecycle used by the implementation: connect handles are created first, domain handles reference connect handles, and account handles reference domain handles. Cache structs are initialized when a domain handle is opened and are cleared/reloaded by enumeration calls.

## State And Persistence

All structures are per-RPC-handle runtime state allocated with talloc and released when the handle is closed or the connection ends. They do not persist data themselves. Persistence happens through the `sam_ctx` LDB context that points at Samba's SAM database. The cache arrays are transient snapshots of enumeration identity, not authoritative object state.

## Dependencies And Integration Points

The header depends on `param/param.h` for loadparm types and `libds/common/roles.h` for `enum server_role`. The declarations also assume LDB, SID, GUID, and generated SAMR NDR types are visible from including source files. It is included by the SAMR endpoint implementation and password code through the local RPC server build.

## Risks And Edge Cases

The state model makes handle-type correctness critical; using the wrong `SAMR_HANDLE_*` value would expose incompatible state through a policy handle. The header stores access masks but does not enforce them by itself, so callers must avoid treating the field as sufficient authorization. Cache memory is tied to domain handles, so long-lived handles doing large enumerations can hold significant transient memory. The `void *sam_ctx` fields in domain/account state are less type-safe than the connect state's `struct ldb_context *`.

## Test Signals

Useful signals are compile-time coverage of all SAMR implementation files, RPC tests that open/close each handle type, invalid-handle-type tests that must fail cleanly, leak checks around repeated connect/open/close/enumerate flows, and enumeration tests proving cache reset and talloc ownership behave correctly across resume handles and handle closure.
