# sources/user-network-fs/samba/source3/lib/sharesec.c

## Purpose
This file manages per-share security descriptors stored in `share_info.tdb`, provides default share ACLs, checks share access against security tokens, and parses usershare ACL strings.

## Important APIs, Types, And Functions
`share_info_db_init()` opens and upgrades the global `share_db`. Versions move through V1/V2/V3, with V3 canonicalizing share names under `SECDESC/`. `get_share_security()` fetches and unmarshals a descriptor or returns a default Everyone descriptor. `set_share_security()` marshals and stores a descriptor transactionally. `delete_share_security()` removes a descriptor. `share_access_check()` calls `se_file_access_check()`. `parse_usershare_acl()` parses strings like `SID:F`, `SID:R`, or `SID:D` into a security descriptor.

## Control Flow
Initialization opens `state_path("share_info.tdb")`, starts a transaction for upgrades, deletes unknown old-version contents, rewrites V2 keys to canonical names, and commits V3. Fetch/set/delete canonicalize service names before building keys. Usershare ACL parsing counts comma-separated ACEs, parses SIDs and access letters, maps generic access through `file_generic_mapping`, and builds an ACL/security descriptor.

## State And Persistence
The global `share_db` caches the database handle. Durable state is tdb records with key `SECDESC/<canonical_share>` and marshalled self-relative security descriptors plus `INFO/version`.

## Dependencies And Integration Points
It depends on dbwrap, state paths, security descriptor NDR marshalling, generic file mapping, SID parsing, and security-token access checks. It integrates with share management, usershares, and SMB tree-connect authorization.

## Risks And Test Signals
Risks include upgrade transaction failure, duplicate canonical names during V2-to-V3 migration, fallback-to-open-default on corrupt descriptors, global handle lifetime, and ACL parser strictness. Tests should cover DB version upgrades, mixed-case share canonicalization, corrupt/missing descriptor fallback, set/get/delete round trips, access allow/deny decisions, empty usershare ACL default read, malformed ACL strings, and deny ACE parsing.
