# sources/user-network-fs/samba/source3/include/idmap_autorid_tdb.h

## Purpose
`idmap_autorid_tdb.h` declares common TDB-backed helpers for the autorid idmap backend and related administration tools. Autorid assigns deterministic ranges to domain SID plus domain-range-index pairs and tracks allocation high-water marks.

## Important APIs, Types, And Functions
- Database keys include `NEXT RANGE`, `NEXT ALLOC UID`, `NEXT ALLOC GID`, `ALLOC`, and `CONFIG`.
- `struct autorid_global_config` stores minimum id value, range size, and max range count.
- `struct autorid_range_config` stores domain SID string, range number, domain range index, and low/high Unix IDs.
- Range APIs get, set, acquire, and delete domain/index-to-range mappings by SID or range number.
- HWM and database APIs initialize/open autorid databases and high-water marks.
- Config APIs load/save/parse/render global configuration.
- Iteration APIs traverse or delete all ranges for a domain in read-write or read-only modes.

## Control Flow
Callers open or initialize a dbwrap database, load config, resolve a domain range with `idmap_autorid_get_domainrange()`, and when not read-only, acquire a new range by incrementing the range HWM. Administration paths can set/delete ranges, initialize allocation HWMs, and iterate per-domain mappings.

## State And Persistence
Persistent state lives in the autorid TDB: config string, next range, next uid/gid allocation HWMs, and range mapping records. The header declares operations that must preserve consistency between SID-index and range-number lookup records.

## Dependencies And Integration Points
It integrates with source3 includes, dbwrap/dbwrap_open, util_tdb, idmap_tdb_common, winbind idmap backends, and `net idmap autorid` utilities.

## Risks
Range acquisition is concurrency-sensitive and must be transactional in implementations. Deleting with `force` can remove invalid records but risks losing forensic data. Config parsing must reject malformed values that could overlap id ranges.

## Test Signals
Test database init/open, HWM initialization and incrementing, get existing range vs acquire new, read-only behavior, duplicate setrange conflicts, delete by SID/range with force true/false, config parse/save/load, and iteration counts.
