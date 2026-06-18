# File Research: sources/os/linux/linux-stable/fs/nfs/nfs4namespace.c

This file implements NFSv4 namespace handling: referral following, security negotiation after `WRONGSEC`, server-name parsing, and transport replacement for migration.

Path helpers:
- `nfs4_pathname_len()` validates and computes POSIX path length from NFSv4 pathname components.
- `nfs4_pathname_string()` converts NFSv4 path components to a slash-prefixed string.
- `nfs_path_component()` extracts the path part from `server:path`, including bracketed IPv6 handling.
- `nfs4_path()` obtains a canonical NFS path and returns the export path component.
- `nfs4_validate_fspath()` verifies that a referral fs_root is a prefix of the current dentry path.

Server-name parsing:
- `nfs_parse_server_name()` tries:
  - `rpc_pton()`
  - `rpc_uaddr2sockaddr()`
  - DNS resolution through `nfs_dns_resolve_name()`
- Applies port when requested.

Security negotiation:
- `nfs_find_best_sec()` selects the first locally supported server-provided security flavor that matches mount `sec=` constraints.
- It clones an RPC client with that auth flavor and verifies credentials can be acquired.
- `nfs4_negotiate_security()` calls `SECINFO` and returns a temporary RPC client with the selected auth flavor.

Referral handling:
- `try_location()` attempts a single fs_locations entry across its server list.
  - Builds hostname, export path, and `fc->source`.
  - Skips scoped IPv6 names.
  - Resolves address and tries `nfs4_get_referral_tree()`.
- `nfs_follow_referral()` validates fs path and iterates fs_locations.
- `nfs_do_refmount()` gets fs_locations for a referral dentry and follows it.
- `nfs4_submount()` re-lookups a mountpoint, determines selected auth flavor, and either follows referral or performs ordinary submount.

Migration transport replacement:
- `nfs4_try_replacing_one_location()` tries servers from a location and calls `nfs4_update_server()`.
- `nfs4_replace_transport()` iterates fs_locations and tries replacement until one succeeds.

Risk areas:
- Referral path validation prevents mounting unrelated server paths.
- `fc->source`, hostname, export path, and server address fields are mutated during location attempts.
- Temporary cloned RPC clients from security negotiation must be shut down by callers.
- IPv6 scoped addresses are intentionally skipped in referral/migration server lists.
