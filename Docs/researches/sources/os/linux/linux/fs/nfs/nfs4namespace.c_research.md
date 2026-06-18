# File Research: sources/os/linux/linux/fs/nfs/nfs4namespace.c

This file implements NFSv4 namespace handling: referral following, `WRONGSEC` security negotiation, server-name parsing, and transport replacement for migration.

Path helpers:
- `nfs4_pathname_len()` validates NFSv4 pathname components against `NAME_MAX` and total rendered length against `PATH_MAX`.
- `nfs4_pathname_string()` converts NFSv4 pathname components into a slash-prefixed POSIX path string.
- `nfs_path_component()` extracts the path part from `server:path`, including bracketed IPv6 address handling.
- `nfs4_path()` obtains a canonical NFS path and returns its export path component.
- `nfs4_validate_fspath()` verifies that a referral `fs_root` is a prefix of the current dentry path.

Server-name parsing:
- `nfs_parse_server_name()` tries `rpc_pton()`, then `rpc_uaddr2sockaddr()`, then DNS resolution through `nfs_dns_resolve_name()`.
- When a numeric address is parsed and a port is supplied, it applies the requested port.

Security negotiation:
- `nfs_find_best_sec()` selects the first server-provided security flavor that is locally supported and matches mount `sec=` constraints, then clones an RPC client with that auth flavor and verifies credentials can be acquired.
- `nfs4_negotiate_security()` calls `SECINFO` for a lookup name and returns a temporary RPC client using the chosen flavor. Callers must shut it down.

Referral handling:
- `try_location()` mutates the mount context for a single `fs_locations` entry, building hostname, export path, `fc->source`, server address, and port before trying `nfs4_get_referral_tree()`.
- It skips server names with IPv6 scope delimiters.
- `nfs_follow_referral()` validates the fs path prefix and iterates locations until one succeeds.
- `nfs_do_refmount()` obtains `fs_locations` for a referral dentry and follows them.
- `nfs4_submount()` re-lookups the mountpoint to get selected auth flavor and attributes, then either follows a referral or performs an ordinary submount.

Migration transport replacement:
- `nfs4_try_replacing_one_location()` allocates a `sockaddr_storage`, iterates usable server names in a location, resolves each name, builds a temporary hostname with `kmemdup_nul()`, and calls `nfs4_update_server()`.
- `nfs4_replace_transport()` iterates fs_locations and tries replacement until one succeeds.
- In this tree, transport replacement does not allocate or pass scratch pathname pages into `nfs4_try_replacing_one_location()`.

Risk areas:
- Referral path validation prevents mounting unrelated server paths from a malicious or stale `fs_locations` result.
- `fc->source`, hostname, export path, selected flavor, and server address fields are mutated during location attempts.
- Temporary cloned RPC clients from security negotiation must be shut down by callers.
- IPv6 scoped addresses are intentionally skipped in referral and migration server lists.
- Migration replacement depends on `nfs4_update_server()` preserving server list membership and reprobe behavior on failure/success.
