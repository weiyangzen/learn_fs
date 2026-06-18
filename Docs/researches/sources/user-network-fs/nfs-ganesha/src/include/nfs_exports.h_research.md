# sources/user-network-fs/nfs-ganesha/src/include/nfs_exports.h

## Purpose

`nfs_exports.h` declares export-list configuration, access-option masks, export-root initialization, export reload/free routines, export security checks, and export logging helpers.

## Important APIs, Types, and Functions

Key types are `global_export_perms`, `exportlist_client_entry`, `client_ha_proxy_protocol_type`, and `log_exports_parms`. The many `EXPORT_OPTION_*` masks describe filesystem ID, caching, max I/O, security labels, squashing, read/write/metadata access, privileged ports, commit, ACL, auth flavors, protocols, transports, delegations, managed gids, and readdirplus. APIs include `get_anonymous_uid`, `get_anonymous_gid`, `export_check_access`, `export_check_security`, `init_export_root`, `nfs_export_get_root_entry`, `release_export`, `ReadExports`, `reread_exports`, `free_export_resources`, `exports_pkginit`, `log_an_export`, and `export_check_options`.

## Control Flow

Startup/reload parses export config into global and per-client permissions, initializes export roots, builds pseudo exports, and validates client security/access on each request. `export_can_be_mounted` filters NFSv4 mountable exports by protocol support, pseudo path, nonzero export ID, and non-root pseudopath.

## State and Persistence Behavior

Exports, client permission lists, locks, root object references, and parsed config are process state. Persistent filesystem data stays in FSALs; export reload can change client-visible access, file handles, and pseudo filesystem topology.

## Dependencies and Integration Points

It depends on config parsing, client/export managers, FSAL types, logging, GSS, and pthread locks. It integrates with NFS credentials, file handle export IDs, MOUNT export lists, pseudo FS, DBus/admin reload, and QoS export classes.

## Risks and Test Signals

Risks include bitmask collisions, incorrect squash/access precedence, reload races under `export_opt_lock`, stale root refs, protocol/transport mismatch, HA proxy policy mistakes, and logging exposure of sensitive paths. Tests should parse all export options, evaluate client-specific permissions, validate auth flavor and privileged-port checks, reload exports under traffic, verify mountability, and ensure root object release/free behavior.
