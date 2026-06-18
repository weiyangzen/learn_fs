# sources/user-network-fs/samba/source3/winbindd/idmap_autorid.c

## Purpose

`sources/user-network-fs/samba/source3/winbindd/idmap_autorid.c` implements the `autorid` idmap backend. It algorithmically maps domain SID/RID ranges to Unix IDs while automatically allocating numeric ranges per domain and preserving special allocation-pool mappings in `autorid.tdb`. The source was read as a complete 945-line file.

## Important APIs, Types, and Functions

Key functions include `idmap_autorid_init`, `idmap_autorid_initialize`, `idmap_autorid_allocate_id`, `idmap_autorid_unixids_to_sids`, `idmap_autorid_sids_to_unixids`, `idmap_autorid_id_to_sid`, `idmap_autorid_sid_to_id`, `idmap_autorid_sid_to_id_alloc`, `idmap_autorid_sid_to_id_special`, `idmap_autorid_preallocate_wellknown`, and `idmap_autorid_initialize_action`. Important globals are `autorid_db` and `ignore_builtin`; `IDMAP_AUTORID_ALLOC_RESERVED` reserves high IDs in the allocation range.

## Control Flow

Initialization only accepts the default `*` idmap domain, builds an `idmap_tdb_common_context`, reads `rangesize` and `ignore builtin`, computes `maxranges`, opens `state_path("autorid.tdb")`, initializes HWMs/config in a transaction, and preallocates well-known group SIDs. SID-to-ID mapping splits the RID, derives domain range index, finds or allocates an autorid range, and computes `id = reduced_rid + range_low_id`. ID-to-SID mapping reverses the calculation by looking up the stored range-number-to-domain record. Well-known/allocated SIDs use the tdb-common allocation pool.

## State and Persistence Behavior

Persistent state lives in `autorid.tdb`: domain/range assignments, configuration, high-water marks, and explicit allocation-pool mappings. The backend writes new ranges and mappings unless `dom->read_only` is true. Runtime state is the shared DB context and global config under `dom->private_data`.

## Dependencies and Integration Points

It depends on `idmap_autorid_tdb` helpers, `idmap_tdb_common`, winbind domain knowledge, samlogon cache, machine SID/passdb checks, SID utility helpers, and the idmap backend registration API.

## Risks and Edge Cases

Incorrect `rangesize` or idmap range configuration can exhaust ranges or fail initialization; at least two ranges are required. Unknown domains are not allocated unless validated by local/builtin/own-domain checks, existing range zero, caller type hints, or samlogon cache. Read-only mode suppresses allocation. ID boundary checks must avoid off-by-one errors near max range. Special SID allocation scans only the reserved top 500 IDs.

## Test Signals

Tests should cover initialization constraints, range-size math, persistence in `autorid.tdb`, SID-to-ID and ID-to-SID round trips across multiple domain range indexes, read-only behavior, unknown-domain `ID_REQUIRE_TYPE`, builtin ignore mode, allocation-pool mappings, well-known preallocation, and database corruption/invalid-record handling.
