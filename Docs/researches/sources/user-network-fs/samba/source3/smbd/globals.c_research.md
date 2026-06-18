# sources/user-network-fs/samba/source3/smbd/globals.c

## Purpose
`globals.c` defines smbd process-global variables declared in `globals.h` and provides small initialization/accessor helpers. It centralizes state shared by many smbd modules: mangling state, memcache, security context stacks, connection context stacks, global SMBXSRV client pointer, encryption contexts, VFS backend list, reload timestamps, and request GUID derivation.

## Important APIs, Types, And Functions
Global definitions include `mangle_fns`, `chartest`, `tdb_mangled_cache`, `mangle_prefix`, `common_flags2`, `sec_ctx_stack`, `conn_ctx_stack`, `smbd_memcache_ctx`, `global_smbXsrv_client`, and related flags/counters. `smbd_memcache()` lazily allocates a process-global memcache under the NULL talloc context sized by `lp_max_stat_cache_size()*1024`; allocation failure calls `smb_panic()`. `smbd_init_globals()` zeroes the security and connection context stacks at startup. `smbd_request_guid()` builds a deterministic GUID-like value from an SMB1 request mid, SMB2 compound index or SMB1 parameter pointer, a caller-supplied index, and connection channel id.

## Control Flow
Most state is initialized by static C initialization. Runtime initialization calls `smbd_init_globals()` to clear context stacks. Callers that need memcache use `smbd_memcache()`, which creates the cache on first use and then returns the same pointer. Request GUID creation is stateless other than reading fields from `smb_request` and `xconn`.

## State And Persistence
All state is process memory. The memcache is intentionally allocated under NULL rather than autofree to avoid fork-child exit side effects. Mangling cache pointers may refer to internal TDB/memcache structures initialized elsewhere. Security and connection stacks are fixed-size arrays tied to `MAX_SEC_CTX_DEPTH`. No on-disk persistence is implemented in this file.

## Dependencies And Integration Points
This file depends on loadparm for memcache sizing, the memcache library, messages/TDB headers, SMB request structures, and protocol constants. Its globals are consumed by name mangling, path lookup caches, authentication/security context switching, VFS backend registration, trans encryption, and SMBXSRV connection/client code.

## Risks
Global mutable state creates ordering and lifetime risks, especially with forked processes and NULL-context allocations. `smbd_memcache()` panics on allocation failure rather than returning an error, so callers assume availability. `smbd_request_guid()` is a correlation identifier built from request metadata rather than a random GUID; consumers must not treat it as cryptographically unique.

## Test Signals
Tests should verify lazy memcache allocation size and reuse, panic behavior under forced allocation failure if supported, `smbd_init_globals()` clearing stack state, and `smbd_request_guid()` stability across SMB1, SMB2 compound indices, different mids, and different channel ids.
