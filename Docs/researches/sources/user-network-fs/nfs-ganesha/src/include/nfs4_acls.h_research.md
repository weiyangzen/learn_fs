# sources/user-network-fs/nfs-ganesha/src/include/nfs4_acls.h

## Purpose

`nfs4_acls.h` declares the FSAL-side NFSv4 ACL cache/allocation interface. It provides allocation, reference management, cache entry creation, and package initialization for ACL data used by NFSv4 attributes and FSAL objects.

## Important APIs, Types, and Functions

`fsal_acl_status_t` status values distinguish success, generic error, existing entry, internal error, inappropriate key, hash set failure, init-entry failure, and not-found. APIs include `nfs4_acl_alloc`, `nfs4_ace_alloc`, `nfs4_acl_free`, `nfs4_ace_free`, `nfs4_acl_entry_inc_ref`, `nfs4_acl_new_entry`, `nfs4_acl_release_entry`, and `nfs4_acls_init`.

## Control Flow

Callers allocate ACE arrays and ACL objects, normalize them into cached ACL entries with `nfs4_acl_new_entry`, increment references when sharing entries, and release entries when FSAL attributes or cache records are dropped.

## State and Persistence Behavior

ACL data is runtime memory and likely hash-table backed in the implementation. Persistent ACL storage remains in the lower filesystem/FSAL; this layer manages in-memory sharing and lifetime.

## Dependencies and Integration Points

The header depends on `fsal_types.h` for `fsal_acl_t`, `fsal_ace_t`, and `fsal_acl_data_t`. It integrates with NFSv4 attribute encode/decode, FSAL ACL support checks, and `COMPONENT_NFS_V4_ACL` logging.

## Risks and Test Signals

Risks include refcount leaks, duplicate ACL canonicalization mistakes, hash collisions, status codes not translated to protocol errors, and ACE count allocation overflow. Tests should allocate/free empty and large ACLs, deduplicate identical ACL data, verify refcount release, inject hash/allocation failures, and perform NFSv4 GETATTR/SETATTR ACL round trips.
