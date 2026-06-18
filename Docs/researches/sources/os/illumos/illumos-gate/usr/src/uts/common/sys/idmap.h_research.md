# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/idmap.h

This header defines status codes and reserved identifiers for illumos ID mapping, especially Windows SID to Unix UID/GID mapping.

Key definitions:
- Success/iteration codes: `IDMAP_SUCCESS`, `IDMAP_NEXT`.
- Error code range from `IDMAP_ERR_OTHER` through `IDMAP_ERR_NO_ACTIVEDIRECTORY`, covering internal/memory/no-result/type/rule/cache/db/argument/SID/RPC/client/busy/permission/no-mapping/domain/security/config/network/LDAP/AD errors.
- Reserved well-known GIDs and UIDs for Local System, Creator Group, and Creator Owner.
- Reserved SID authority: `IDMAP_WK_CREATOR_SID_AUTHORITY`.
- Door RPC size cap: `IDMAP_MAX_DOOR_RPC` at 256 KiB.
- `IDMAP_SENTINEL_PID` and `IDMAP_ID_IS_EPHEMERAL(pid)` macro.

Relevance:
- Important to SMB/NFS identity translation and access control around filesystems.
- This file is constants only; no functions or structures are declared.
