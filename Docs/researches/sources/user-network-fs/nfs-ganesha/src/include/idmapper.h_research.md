# sources/user-network-fs/nfs-ganesha/src/include/idmapper.h

## Purpose

`idmapper.h` is the public and semi-private declaration point for Ganesha's ID mapper. It binds numeric UID/GID values, group lists, GSS principals, and NFSv4 owner/group strings together for protocol request handling. The header also exposes cache lifecycle APIs and DBus cache inspection hooks.

## Important APIs, Types, and Functions

The cache API is split between positive caches (`idmapper_add_user`, `idmapper_add_group`, lookup by name/id) and negative caches (`idmapper_negative_cache_add_*`, lookup, clear, destroy, reap). The five exported `pthread_rwlock_t` objects protect user, group, and negative-cache maps shared by `idmapper.c` and `idmapper_cache.c`. Public conversion APIs include `name2uid`, `name2gid`, `xdr_encode_nfs4_owner`, `xdr_encode_nfs4_group`, and optional `_HAVE_GSSAPI` `principal2uid`. `PWENT_BEST_GUESS_LEN`, `PWENT_MAX_SIZE`, and `GROUP_MAX_SIZE` bound passwd/group-entry buffer growth.

## Control Flow

Typical NFSv4 processing decodes an owner string with `name2uid` or encodes numeric IDs with the XDR helpers. The implementation first consults idmapper caches, may call libc/nfsidmap/winbind/GSS backends, inserts success or negative results, and exposes periodic cleanup through `idmapper_cache_reap` and `idmapper_negative_cache_reap`.

## State and Persistence Behavior

State is in process memory only: positive maps, negative maps, and timing/stat counters. `idmapper_clear_cache` and `idmapper_destroy_cache` are explicit invalidation/lifetime controls; no durable mapping database is declared here.

## Dependencies and Integration Points

The header depends on `gsh_rpc.h`, `gsh_types.h`, XDR, POSIX IDs, pthread locks, optional GSSAPI/MSPAC, optional DBus, and monitoring update functions for winbind, group-cache, and DNS latencies. It integrates with NFSv4 ACL/attribute encoding, credential establishment, and admin cache diagnostics.

## Risks and Test Signals

Risks are stale mappings, negative-cache poisoning after directory-service recovery, lock-order bugs across user/group caches, huge passwd/group records up to 64 MiB, and GSS conditional ABI differences. Tests should cover cache hit/miss/reap paths, name/domain variants, unmapped names, principal mapping with and without MSPAC, DBus cache display, cache clear during live requests, and owner/group XDR round trips.
