# sources/user-network-fs/nfs-ganesha/src/include/fsal_types.h

Purpose: This is the shared FSAL type vocabulary for object kinds, credentials, export permissions, ACLs, attributes, status codes, filesystem capabilities, quotas, locking, open/share state, and generic FD coordination.

Important APIs/types/functions: `object_file_type_t`, `struct user_cred`, `struct export_perms`, `fsal_fsid_t`, `fsal_dev_t`, ACL structs/macros, `attrmask_t` and `struct fsal_attrlist` define metadata surfaces. `fsal_accessflags_t`, `fsal_openflags_t`, create/readdir modes, `fsal_staticfsinfo_t`, `fsal_status_t`, `fsal_dynamicfsinfo_t`, quota, lock/share/delegation types, `struct fsal_fd`, `init_fsal_fd`, `destroy_fsal_fd`, and `struct fsal_share` define operational state.

Control flow: FSAL methods receive requested masks, fill valid masks, return `fsal_status_t`, and use capability booleans to drive protocol behavior. FD helpers initialize mutex/condition-backed descriptors used by FSAL FD management and LRU reclaim.

State and persistence: Attribute structs carry NFS-visible metadata, ACL references have locks/refcounts, fsids/fileids form stable identity, static fsinfo describes per-export durable capability policy, and FD/share structures track active open/share state.

Dependencies and integration points: Depends on `nfsv41.h`, pthread primitives, XDR-related constants, op context through `FSAL_FD_INIT`, and list utilities. It is included by most FSAL and protocol bridge headers.

Risks: Mask misuse is the main hazard: setting bits without valid data or omitting supported masks changes client-visible behavior. ACL reference locking, FD condition variables, and share counters must remain balanced. `FSAL_MAXIOSIZE` ties IO limits to RPC/XDR caps.

Test signals: Validate attribute masks, ACL inheritance/evaluation, status mapping, open/share deny matrix, fd init/destroy for temp and non-temp descriptors, static fsinfo feature queries, quota/lock/delegation conversions, and NFSv3/v4 metadata encoding.
