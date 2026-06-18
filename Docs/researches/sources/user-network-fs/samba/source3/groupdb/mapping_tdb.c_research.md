# sources/user-network-fs/samba/source3/groupdb/mapping_tdb.c

## Purpose
`mapping_tdb.c` implements the `mapping_backend` contract using Samba's dbwrap/TDB layer. It stores SID-to-group mappings in `group_mapping.tdb`, maintains reverse alias membership records, and converts an older `group_mapping.ldb` store into the TDB format on first initialization.

## Important APIs, Types, And Functions
- Static `db` is the opened `db_context` for `group_mapping.tdb`.
- `init_group_mapping()` opens the TDB database and performs legacy LDB conversion if `group_mapping.ldb` exists.
- `group_mapping_key()` builds `UNIXGROUP/<sid>` keys.
- `add_mapping_entry()`, `get_group_map_from_sid()`, `get_group_map_from_gid()`, `get_group_map_from_ntname()`, `group_map_remove()`, and `enum_group_mapping()` implement mapping CRUD and traversal.
- `dbrec2map()`, `find_map()`, and `collect_map()` unpack dbwrap records into `GROUP_MAP` structures and filter them.
- `one_alias_membership()`, `alias_memberships()`, `is_aliasmem()`, `add_aliasmem()`, `enum_aliasmem()`, and `del_aliasmem()` manage reverse membership records.
- `convert_ldb_record()` and `mapping_switch()` read raw LDB/TDB records, convert attributes into group maps and alias membership, then rename the old database.
- `groupdb_tdb_init()` exposes the static `tdb_backend` function table.

## Control Flow
Initialization opens `state_path("group_mapping.tdb")` with `O_RDWR|O_CREAT`. If `group_mapping.ldb` exists, `mapping_switch()` opens it read-only, traverses every record with `convert_ldb_record()`, writes converted maps and memberships to the new TDB, closes the old database, and renames it to `group_mapping.ldb.replaced`. Otherwise historic version-upgrade code is currently disabled.

Direct SID lookup fetches one key and unpacks `"ddff"` into gid, SID name use, NT name, and comment. Gid and NT-name lookup traverse all records. Enumeration traverses all records and filters by SID type, mapped-only mode, and domain SID. Alias membership stores a member-keyed list of alias SIDs. Adding membership verifies the alias exists and has alias/well-known group type, checks duplicates, locks the member record inside a transaction, appends the alias SID string, stores, and commits. Deleting membership reads current aliases, removes the target, deletes the record if empty or rewrites the space-separated list, then commits.

## State And Persistence
Persistent state lives in `group_mapping.tdb`. Group records are keyed by `GROUP_PREFIX + SID`; alias membership records are keyed by `MEMBEROF_PREFIX + member SID`. Membership values are plain space-separated SID strings. Transactions are used for alias add/delete. Conversion from LDB is persistent and destructive in the sense that the old file is renamed after successful conversion.

## Dependencies And Integration Points
This file depends on dbwrap, TDB, Samba state paths, tdb pack/unpack helpers, SID utilities, passdb `GROUP_MAP`, and the `mapping_backend` interface. Its performance matters during session setup because alias membership checks are called while building tokens.

## Risks
- `add_mapping_entry()` ignores its `flag` argument and always uses `TDB_REPLACE`, so insert-only semantics requested by callers are not enforced.
- Gid and NT-name lookups are full database traversals.
- Alias membership values are string lists; corruption, duplicate whitespace, or partial writes outside transactions can affect parsing.
- `add_aliasmem()` starts a transaction but returns immediately on transaction commit failure without cancel cleanup, which is typical after failed commit but should be understood.
- LDB conversion parses raw packed data and is sensitive to bounds; it sets `errno` and returns failure on malformed input but may have partially written earlier converted records before a later failure.
- Disabled version-upgrade cleanup means old version handling may not run through dbwrap.

## Test Signals
Test database open/create failures, exact key formation, add vs replace behavior, direct SID lookup, traversal lookup by gid/name, enum filters, mapped-only filtering, alias duplicate add, delete missing member, delete last member removing the record, LDB conversion success and malformed records, transaction failure injection, and migration rename behavior.
