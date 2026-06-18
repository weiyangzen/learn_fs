# sources/user-network-fs/samba/source3/nmbd/nmbd_serverlistdb.c

## Purpose
`nmbd_serverlistdb.c` manages per-workgroup server records and writes Samba's browser service list cache. It adds, updates, expires, removes, de-duplicates, and serializes `server_record` entries into `browse.dat`.

## Important APIs, types, and functions
- `remove_all_servers`, `remove_server_from_workgroup`, `create_server_on_workgroup`, `find_server_in_workgroup`, `update_server_ttl`, and `expire_servers` manage server lists.
- `write_browse_list_entry` writes one formatted row.
- `write_browse_list` writes the derived browser cache.
- `updatecount` is the browser update counter used by announcement code.

## Control flow
Announcements and syncs create/update records through this file. TTL updates clamp remote records and keep Samba-owned names permanent. `write_browse_list` throttles unless forced, dumps workgroups, checks change flags, writes a temporary cache file, outputs local workgroup and local names, then walks all subnets/workgroups/servers while suppressing duplicates.

## State and persistence behavior
Runtime state lives in `work_record->serverlist` and `subnet_record->work_changed`. The derived persistent view is written to `cache_path(SERVER_LIST)` by unlink/rename of a temporary file. Change flags are cleared after writing.

## Dependencies and integration points
The file integrates with workgroup lookup, local name enumeration, service type constants, loadparm server-string substitution, cache-path helpers, and announcement code through `updatecount`.

## Risks and edge cases
The text output format is legacy and field-sensitive. Duplicate suppression favors broadcast-subnet records over unicast sync records. Cache replacement does not fsync. Duplicate server creation is treated as a bug rather than an update.

## Test signals
Cover TTL clamping/expiration, duplicate suppression across subnets, self-name merge behavior, `work_changed` writes, forced writes, and `browse.dat` formatting.
