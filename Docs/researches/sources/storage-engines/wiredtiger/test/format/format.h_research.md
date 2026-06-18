# sources/storage-engines/wiredtiger/test/format/format.h

## Purpose
`format.h` is the central contract for the WiredTiger format test program. It defines shared constants, generated configuration integration, table/global runtime state, worker thread state, operation enums, and prototypes used across the format source tree.

## Important APIs, Types, And Functions
Key types are `CONFIGV`, `LANE`, `READ_SCAN_ARGS`, `RWLOCK`, `SAP`, `TABLE`, `DISAGG_MULTI_DB_HASH`, `GLOBAL`, `SNAP_OPS`, `SNAP_STATE`, and `TINFO`. Important macros include extension library paths, `BACKUP_INFO_FILE`, `BACKUP_MAX_COPY`, `FORMAT_OPERATION_REPS`, `SESSION_PREFETCH_CFG_*`, `GV/GVS/NTV/NTVS/TV/TVS`, trace flags, checkpoint constants, and `LANE_NUMBER`. It declares all major worker and utility functions.

## Control Flow
The header itself has no runtime flow, but it shapes the program: configuration values live in `tables[0]` for globals and defaults, table-specific values live in `tables[1..ntables]`, workers use `GLOBAL g`, and operation threads use `TINFO` snapshots/cursors/counters. Including `format_inline.h` at the end makes common operations inline across all format files.

## State And Persistence Behavior
`GLOBAL` owns connection handles, home paths, backup IDs, RNG state, timestamp state, disaggregated multi-node handles, checkpoint metadata, and mode booleans. `TABLE` owns URI, type, row counts, key/value generation state, mirror flag, page sizing, and the full `CONFIGV` array. These structures are in-memory, while selected fields drive persisted `CONFIG`, backup metadata, checkpoints, and WiredTiger metadata.

## Dependencies And Integration Points
It depends on WiredTiger internal/test headers through `test_util.h`, generated `format_config.h`, POSIX signal/socket/resource headers, and pthread/WiredTiger lock APIs. It is included by every researched C file and is the integration point among config parsing, workload operations, backup, checkpoint, compaction, disaggregation, timestamping, replay, tracing, and verification.

## Risks And Test Signals
Risks are macro misuse across global/table offsets, assumptions about table slot 0, shared global state races, and ABI drift between generated config offsets and `CONFIGV` arrays. Compile errors, assertion failures in accessor helpers, and inconsistent config dumps are the strongest signals of contract breakage.
