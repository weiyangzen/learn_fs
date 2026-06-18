# sources/storage-engines/rocksdb/utilities/backup/backup_engine_impl.h

## Purpose

This internal header exposes test-only hooks for the backup engine implementation. It is not the public backup API; it lets tests force metadata schema variants and control clocks in default rate limiters.

## Important APIs, types, and functions

`TEST_BackupMetaSchemaOptions` carries a schema `version`, booleans controlling crc32c checksum and size field emission, and maps for extra meta, file, and footer fields. `TEST_SetBackupMetaSchemaOptions` installs those options on a `BackupEngine`. `TEST_SetDefaultRateLimitersClock` replaces clocks used by default-created backup and restore rate limiters.

## Control flow

The header declares hooks implemented at the end of `backup_engine.cc`. The schema hook downcasts to `BackupEngineImplThreadSafe` and stores options that `BackupMeta::StoreToFile` reads while writing metadata. The clock hook downcasts and calls through to `GenericRateLimiter::TEST_SetClock` for backup and restore limiters when provided.

## State and persistence behavior

The schema options affect subsequent backup meta-file persistence for the lifetime of the engine object, not for the whole backup directory. They can force unpublished schema version 2 behavior, omit checksums, include sizes, and inject unrecognized or non-ignorable fields. The rate-limiter clock hook changes in-memory limiter timing for tests only.

## Dependencies and integration points

It includes `rocksdb/utilities/backup_engine.h` for `BackupEngine` and uses `SystemClock` through the public backup-engine dependency chain. Tests in `backup_engine_test.cc` and DB stress code include these hooks to cover metadata forward-compatibility, schema rejection, and faster deterministic rate limiter behavior.

## Risks

These hooks rely on downcasting the public engine pointer to the internal implementation wrapper, so they are only valid for engines created by this implementation. Misuse outside tests can write unusual metadata files into real backup directories. The defaults are intentionally test-oriented (`crc32c_checksums=false`, `file_sizes=true`) and differ from normal production metadata writing.

## Test signals

Schema tests use this header to validate metadata parser behavior for missing checksums, size fields, custom fields, footer fields, non-ignorable future fields, and unsupported versions. Rate limiter tests use the clock hook to avoid slow wall-clock waits.
