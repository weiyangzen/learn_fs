# sources/user-network-fs/samba/source3/include/ntquotas.h

## Purpose
`ntquotas.h` defines Windows NT quota flags, quota sentinel values, quota unit constants, quota type identifiers, and in-memory quota record/list/handle structures used by Samba quota handling.

## Important APIs, Types, And Control Flow
Quota flags cover enablement, deny-disk behavior, logging, content indexing, threshold/limit logging, incomplete/rebuilding states, and reserved bits. Sentinel values include no limit, no entry, and no space. Size constants span bytes through exabytes. `enum SMB_QUOTA_TYPE` distinguishes user filesystem quota, user quota, group filesystem quota, and group quota. `SMB_NTQUOTA_STRUCT` stores type, used space, soft/hard limits, flags, and SID. `SMB_NTQUOTA_LIST` links quota records with uid and talloc context. `SMB_NTQUOTA_HANDLE` tracks valid/current/temp lists.

## State And Persistence
The header models quota state returned from or written to system quota backends. Persistence is in filesystem quota systems and Samba quota databases/modules; linked lists and handles are transient enumeration/editing state.

## Dependencies And Integration Points
It depends on domain SID types, talloc, uid_t, and quota system wrappers declared elsewhere. It integrates with NT transact/query quota handlers, disk-free queries, sysquota backends, VFS modules, and Windows clients interpreting quota flags.

## Risks And Test Signals
Risks include sentinel values colliding with real limits, signed/unsigned conversion bugs, unsupported group filesystem quotas, stale temporary list handling, and mismatched flag semantics compared with Windows. Test signals include quota query/set round trips, no-limit/no-entry/no-space cases, large exabyte values, user versus group quota queries, SID-to-uid mapping failures, and backend-specific sysquota tests.
