# sources/user-network-fs/samba/source3/winbindd/idmap_tdb.c

## Purpose
This backend stores writable idmap mappings in the local `winbindd_idmap.tdb` state database. It also upgrades old database formats and initializes UID/GID high-water marks.

## Important APIs, Types, And Functions
Important helpers are `convert_fn`, `idmap_tdb_upgrade`, `idmap_tdb_init_hwm`, `idmap_tdb_open_db`, and `idmap_tdb_db_init`. It configures an `idmap_tdb_common_context` and delegates mapping/allocation to `idmap_tdb_common_*`. `idmap_tdb_init` registers the backend under `tdb`.

## Control Flow
Initialization creates a common context, allocates `idmap_rw_ops`, sets `max_id` and HWM key names, installs common allocation/storage callbacks, stores context in `dom->private_data`, and opens the database. Opening uses `state_path("winbindd_idmap.tdb")`, creates the DB if needed, checks `IDMAP_VERSION`, and runs upgrade in a transaction when needed. Upgrade handles byte-reversed versions, normalizes high-water marks, traverses old `DOMAIN/rid` keys, converts them to SID string keys, updates reverse mappings, deletes old records, and stores version 2. HWM init ensures user/group marks are at least `dom->low_id`.

## State And Persistence
Persistent records include `IDMAP_VERSION`, `USER HWM`, `GROUP HWM`, and bidirectional `SID <-> UID/GID` strings written by `idmap_tdb_common`. The database is local state, not clustered.

## Dependencies And Integration
It uses dbwrap open/transaction/traverse APIs, TDB helpers, domain lookup during upgrade, SID helpers, and common idmap allocation code. It integrates with the Samba idmap registry and default-domain allocator rules in `idmap_tdb_common_get_new_id`.

## Risks And Test Signals
Test new DB creation, HWM initialization below/above low_id, version upgrade, byte-swapped HWM records, old `DOMAIN/rid` conversion, missing domain deletion, reverse mapping replacement, transaction cancel/commit failures, and allocation at high_id. Upgrade mutates keys in traversal and depends on old key string null-termination and slash parsing.
