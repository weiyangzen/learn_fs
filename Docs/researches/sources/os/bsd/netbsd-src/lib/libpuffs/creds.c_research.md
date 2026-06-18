# File Research: sources/os/bsd/netbsd-src/lib/libpuffs/creds.c

This file implements PUFFS credential inspection and generic access checks. It distinguishes user credentials (`PUFFCRED_TYPE_UUC`) from internal credentials (`PUFFCRED_TYPE_INTERNAL`). Accessors return uid, gid, and group lists for regular user credentials, or `EOPNOTSUPP` for unsupported credential types. Predicates check uid equality, group membership, regular/kernel/filesystem credentials, and "juggernaut" privilege, meaning root, kernel, or filesystem credential.

`puffs_access` mirrors kernel `vaccess` behavior: kernel/filesystem credentials bypass checks; root bypasses except for non-directory execute when no execute bit is set; ordinary users are checked against owner, group, or other permission bits according to requested read/write/execute access.

`puffs_access_chown`, `puffs_access_chmod`, and `puffs_access_times` enforce common ownership, group, sticky/setgid, and timestamp permission rules using the credential helpers.

Integration points: used by userspace filesystem implementations that want kernel-like access decisions. Risks are semantic drift from kernel `vaccess`, special treatment of internal credentials, and caller responsibility to pass correct vnode type/mode/owner/group data.
