# sources/user-network-fs/nfs-ganesha/src/support/uid2grp.c

Purpose: resolves users, UIDs, and Kerberos principals to primary and supplementary group lists for request credential handling.

Important APIs, types, and functions: public entry points are `uname2grp`, `uid2grp`, `principal2grp`, `uid2grp_unref`, and refcount helpers. Internal allocation routines call `getpwnam_r`, `getpwuid_r`, `getgrouplist`, and optional `nfs4_gss_princ_to_grouplist`. `uid2grp_sem` throttles directory-service group list requests.

Control flow: lookup first checks `idmapping_enabled`, then the `uid2grp_cache` under read lock. Non-expired cache hits are refcounted and returned. Misses or expired entries allocate fresh `group_data`, fetch passwd and group data, add the new entry to cache under write lock, and remove expired stale entries on failure. UID failures also populate the negative UID cache.

State and persistence: returned `group_data` objects are heap-allocated with embedded user/principal name, group array, primary IDs, epoch, mutex, and refcount. Cache ownership and caller ownership share the same refcount. The data is in-memory and expires based on `manage_gids_expiration`.

Dependencies and integration points: integrates with `uid2grp_cache.c`, idmapper negative cache, pwnam wrappers, `nfs_param.directory_services_param.max_groups_membership`, auth/idmapper monitoring, LTTng tracepoints, optional libnfsidmap, and the global `idmapping_enabled` switch.

Risks: callers must always call `uid2grp_unref` after successful resolution. Directory-service calls can block and are only optionally throttled. `getpwnam_r`/`getpwuid_r` ERANGE paths return without freeing the last allocated buffer in this file's current structure. Cache insertion deliberately rechecks `idmapping_enabled` to avoid repopulating after idmapping disable. Principal lookup uses the principal string as cache uname, so principal and username namespace collisions are possible if upstream callers mix them.

Test signals: useful tests mock pwnam wrappers for success, ENOENT, ERANGE, and large group lists; verify cache hit/refcount behavior; verify stale removal; verify negative cache insertion; and exercise idmapping-disable races.
