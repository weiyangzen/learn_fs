# sources/user-network-fs/nfs-utils/support/export/auth.c

Purpose: `auth.c` authenticates mount requests against the current export table. It normalizes requested paths, resolves clients, reloads exports when state changes, chooses matching exports, and enforces privileged-port restrictions.

Important APIs, types, and functions: `auth_reload()` tracks `etab.statefn` inode changes, calls `export_freeall()`, `xtab_export_read()`, `check_useipaddr()`, and `v4root_set()`, then returns a reload counter. `check_useipaddr()` enables IP-address cache mode when netgroup hostnames would exceed kernel cache name limits. `get_client_hostname()` returns composed client domains, `DEFAULT`, or `$ip` form. `client_matches()`, `ipaddr_client_matches()`, and `namelist_client_matches()` abstract client matching. `auth_authenticate()` is the public entry point.

Control flow: `auth_authenticate()` rejects non-absolute paths, copies and fixes duplicate/trailing slashes, resolves the caller address, then repeatedly tries the longest path prefix by truncating at slashes. `auth_authenticate_internal()` calls `auth_authenticate_newcache()` and rejects high source ports unless the export has `NFSEXP_INSECURE_PORT`. Logging reports distinct auth errors.

State and persistence: static `my_exp` and `my_client` hold the returned export/client data, so the return value is not independently owned. `auth_reload()` keeps the last open etab fd and inode to avoid stale inode reuse, and updates the global export/client lists. It may flush kernel caches when `use_ipaddr` changes.

Dependencies and integration points: depends on export parsing/list structures, client resolution/matching helpers, `cache_flush()`, `v4root_set()`, state file metadata, xlog, and sockaddr utilities. Used by mountd/exportd authentication flows.

Risks: the returned static export is overwritten on subsequent authentication. `auth_reload()` treats unchanged inode as unchanged content, so in-place edits without replacement could be missed if the state workflow allowed them. Long netgroup behavior changes cache keying and flushes caches, which can affect live clients. Privileged-port enforcement depends on caller sockaddr correctness.

Test signals: cover absolute-path validation, duplicate slash cleanup, longest-prefix export matching, netgroup thresholds toggling `use_ipaddr`, V4ROOT exclusion for v2/v3 auth, insecure-port exports, and etab replacement vs unchanged-inode reload behavior.
