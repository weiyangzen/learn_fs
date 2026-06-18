# sources/user-network-fs/samba/source3/librpc/idl/open_files.idl

## Purpose
`open_files.idl` defines serialized structures for Samba open-file/share-mode state, durable handle cookies, lease/oplock break messages, and rename notifications.

## Important APIs, types, and functions
- `share_entry_flags`, `share_mode_entry_op_type`, and `share_mode_entry` describe an opener's PID, MID, oplock/lease type, client GUID, lease key, access/share masks, UID, flags, and name hash.
- `delete_token` and `share_mode_data` define share-mode records including delete security tokens, service path, base/stream names, and cache flags.
- `vfs_default_durable_cookie` stores durable handle reconnect data with a magic string, version, file ID, path, allocation/position/write-time data, and stat snapshot.
- `oplock_break_message` and `file_rename_message` are public messaging payloads.

## Control flow
The IDL models state used by share-mode/open-file code. Open creation inserts records, conflict checks read `share_mode_data`, lease/oplock breaks send message payloads, and durable reconnect validates cookie magic/version and file identity.

## State and persistence behavior
Some fields are stored in TDB-like records, while `[skip]` and `[ignore]` fields are in-memory only. The `stale`, `not_stored`, and `modified` booleans affect cache/writeback behavior but are intentionally excluded from serialized state. Durable cookie versioning and magic protect reconnect parsing.

## Dependencies and integration points
Imports include server IDs, security tokens, file IDs, SMB2 lease keys, and misc time/stat types. Generated NDR feeds the `NDR_OPEN_FILES` subsystem and is used by smbd open/share-mode databases and messaging.

## Risks and edge cases
On-disk compatibility is sensitive: field changes can break durable handles and share-mode records. `name_hash` collision behavior, stale PID filtering, lease state consistency, UTF-8 path encoding, and security token serialization are important. Durable cookies need strict magic/version checks before trust.

## Test signals
Test share-mode serialization round trips, stale entry filtering, delete-on-close token persistence, named stream paths, durable handle reconnect across restart, oplock/lease break message decode, rename messages, and old cookie/version rejection.
