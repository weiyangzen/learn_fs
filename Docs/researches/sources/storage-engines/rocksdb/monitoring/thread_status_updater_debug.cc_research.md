# sources/storage-engines/rocksdb/monitoring/thread_status_updater_debug.cc

Purpose: Provides debug-only validation for the `ThreadStatusUpdater` column-family info map.

Important APIs/types/functions: `ThreadStatusUpdater::TEST_VerifyColumnFamilyInfoMap` checks whether supplied `ColumnFamilyHandle*` entries exist or do not exist in `cf_info_map_` and match CF names.

Control flow: In debug and thread-status-enabled builds, the function locks `thread_list_mutex_`, optionally asserts map size equals handle count, converts handles to `ColumnFamilyHandleImpl`, reads each `ColumnFamilyData`, and asserts map presence/name expectations. Disabled thread-status builds provide an empty body.

State/dependencies: Reads `cf_info_map_` under the updater mutex. Depends on `db/column_family.h`, `util/cast_util.h`, and updater declarations.

Risks/test signals: This is assertion-only debug code and has no runtime behavior in release. It directly supports tests that need lifecycle assurance for CF tracking metadata.
