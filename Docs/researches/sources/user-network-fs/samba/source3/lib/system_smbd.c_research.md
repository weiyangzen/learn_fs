## sources/user-network-fs/samba/source3/lib/system_smbd.c

Purpose: smbd-linked system wrapper focused on Unix group membership lookup for a user without letting winbind remote membership expansion leak into local Unix group enumeration.

Important functions are private `getgrouplist_getgrset`, `getgrouplist_internals`, `sys_getgrouplist`, and public `getgroups_unix_user`. The implementation selects native `getgrouplist` when available, AIX `getgrset` when available, or a root-only `initgroups` fallback.

Control flow: `sys_getgrouplist` temporarily disables winbind environment lookups, performs the platform-specific group-list call, then re-enables winbind only if it was not already disabled. The fallback saves current supplementary groups, calls `initgroups`, sets effective/real gid to the primary gid to normalize returned groups, reads the group list, restores IDs, and restores original groups with `sys_setgroups`, panicking if restoration fails. `getgroups_unix_user` first tries a bounded stack array, reallocates if the platform reports more groups, and then builds a unique talloc-owned group array with the primary gid first.

State and persistence: it temporarily mutates process group credentials and winbind environment state, but intends to restore them before returning. Output groups are talloc-owned. Dependencies are smbd privilege helpers, winbind client toggles, passwd/group APIs, and `sys_setgroups`.

Risks: the fallback is privilege-sensitive and process-global; failure to restore groups is fatal. Disabling winbind can affect concurrent code in the same process. Stack VLA size depends on `getgroups_max` capped to 128. Tests should cover native and fallback paths, duplicate primary gid handling, insufficient buffer retry, winbind on/off restoration, and failure injection for group restoration.
