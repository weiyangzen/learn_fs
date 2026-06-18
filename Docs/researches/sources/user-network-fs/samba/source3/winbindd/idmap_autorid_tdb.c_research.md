# sources/user-network-fs/samba/source3/winbindd/idmap_autorid_tdb.c

## Purpose
This file implements the shared `autorid.tdb` database operations used by the `idmap_autorid` backend and `net idmap autorid` tooling. It manages deterministic domain/range assignments, global autorid configuration, high-water marks, range deletion, and range iteration. The database schema is compact: domain SID keys, optionally suffixed with `#<domain_range_index>`, map to numeric range IDs; numeric range ID keys map back to the domain/index key; `CONFIGKEY` stores `minvalue`, `rangesize`, and `maxranges`; HWM records track the next allocatable range and special allocation pools.

## Important APIs, Types, And Functions
The exported API includes `idmap_autorid_setrange`, `idmap_autorid_acquire_range`, `idmap_autorid_getrange`, `idmap_autorid_get_domainrange`, `idmap_autorid_delete_range_by_sid`, `idmap_autorid_delete_range_by_num`, `idmap_autorid_db_open`, `idmap_autorid_db_init`, `idmap_autorid_init_hwms`, `idmap_autorid_loadconfig`, `idmap_autorid_saveconfig`, `idmap_autorid_saveconfigstr`, `idmap_autorid_iterate_domain_ranges`, `idmap_autorid_iterate_domain_ranges_read`, and `idmap_autorid_delete_domain_ranges`. `struct autorid_range_config` and `struct autorid_global_config` come from `idmap_autorid_tdb.h`.

## Control Flow
Range creation funnels through `idmap_autorid_addrange`, which runs `idmap_autorid_addrange_action` inside `dbwrap_trans_do`. The action validates the domain SID or the special `ALLOC_RANGE`, checks for an existing forward mapping, loads global config, decides the requested or next HWM range, validates capacity and reverse-key availability, increments HWM when needed, then writes both directions. Lookup uses `idmap_autorid_getrange_int`, and `idmap_autorid_get_domainrange` optionally acquires a missing range unless read-only. Delete-by-SID and delete-by-number both validate forward/backward consistency and support `force` to remove partially corrupt mappings. Iteration traverses db records, parses `<sid>[#<index>]`, filters invalid records, and invokes caller callbacks.

## State And Persistence
All persistent state is in a dbwrap/TDB database opened by `idmap_autorid_db_open`. High-water mark initialization is transactional. Range allocation and deletion are transactional, preserving forward/reverse consistency in normal operation. The code intentionally does not shrink HWM on deletion, so deleted ranges are not automatically reused through ordinary allocation. Config changes reject changed `minvalue` or `rangesize`, and reject `maxranges` values below the current HWM.

## Dependencies And Integration
The file depends on `dbwrap`, TDB string helpers, Samba SID parsing/stringification, and constants from `idmap_autorid_tdb.h`. `idmap_autorid.c` uses it during idmap backend initialization and SID/RID mapping. Administrative tooling can use the same APIs to inspect or repair the database.

## Risks And Test Signals
Test database creation, config persistence, duplicate range insertion, explicit range below/above HWM, automatic acquire, capacity exhaustion, `#index` parsing, read-only lookup behavior, forced and non-forced delete of invalid mappings, and iteration over mixed valid/invalid records. Corruption handling is careful but depends on fixed string formats and uint32 value sizes. Capacity exhaustion currently maps to `NT_STATUS_NO_MEMORY`, which can obscure the real cause. Tests should also cover non-null-terminated config data because retrieval uses `talloc_strndup`.
