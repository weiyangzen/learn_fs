# sources/storage-engines/tikv/components/tikv_util/src/config.rs

## Purpose
Provides TiKV's common configuration utility layer: human-readable size, duration, schedule, and log-format types; filesystem and address validation helpers; kernel/data-directory checks; online-config version tracking; TOML patch writing; numeric enum serde generation; and a crash-safe Raft data migration state machine.

## Important APIs, Types, And Functions
`ConfigError` classifies config validation failures into limit, address, store-label, value, and filesystem errors. Unit constants (`B`, `KIB`, `MIB`, `GIB`, `TIB`, `PIB`) and time units back the typed wrappers.

`ReadableSize` parses and serializes byte sizes with binary units, supports integer bytes and floating/scientific values with supported units, and converts to/from `online_config::ConfigValue::Size`. `ReadableSizeOrPercent` extends that behavior for percentage strings resolved against `SysQuota::memory_limit_in_bytes`, while serializing back to an absolute size. `ReadableDuration` wraps `crate::time::Duration`, supports arithmetic, parses ordered `d`, `h`, `m`, `s`, `ms`, and `us` components, serializes to compact strings, and converts to/from `ConfigValue::Duration`.

`ReadableOffsetTime` and `ReadableSchedule` model scheduled clock times with `chrono::NaiveTime` and `FixedOffset`. They parse `HH:MM` with optional timezone offsets, serialize to strings, convert schedule config values, and expose hour or hour-minute matching against arbitrary `DateTime<Tz>`.

Path helpers include `normalize_path`, `canonicalize_path`, `canonicalize_sub_path`, `canonicalize_log_dir`, and `ensure_dir_exist`. Validation helpers include `check_max_open_fds`, `check_kernel`, `check_data_dir`, `check_data_dir_empty`, and `check_addr`.

`VersionTrack<T>` owns a `RwLock<T>` plus an atomic version. `Tracker<T>` is a cloneable consumer-side cursor that returns a read guard from `any_new` only after a successful version bump. `TomlLine` and `TomlWriter` implement targeted TOML key replacement/addition for the limited config-file shapes used by TiKV. `numeric_enum_serializing_mod!` creates serde helpers for enums represented by numeric TOML values while still accepting kebab-case variant strings. `RaftDataStateMachine` coordinates safe migration between source and target Raft data directories.

## Control Flow
Readable parsers split numeric prefixes from unit suffixes, validate ASCII input, and produce deterministic error strings for unsupported units or ordering. Duration parsing walks the input from larger to smaller units and rejects repeated/out-of-order units.

Path canonicalization first normalizes components, then canonicalizes the longest physically existing prefix so non-existing final paths can still become stable absolute paths. `canonicalize_sub_path` rejects existing files where directories are expected, while `canonicalize_log_dir` allows a direct file path but rejects a final directory.

Linux data-dir checking resolves the real path, finds the longest matching mount entry via `getmntent`, logs filesystem information, and warns when the block device reports rotational media. Kernel checks iterate a fixed `/proc/sys` table and collect, rather than short-circuit, all failed checks.

Online config updates call a caller-supplied closure under the write lock. Only successful closures increment the version. Trackers compare their remembered version with the atomic version, try a non-blocking read first, and slow-log if they must block on the read lock.

`TomlWriter::write_change` scans source lines, tracks the current table, replaces matching key/value lines, injects pending keys before leaving a table, and creates missing table sections for remaining dotted keys. It intentionally supports only common TiKV config TOML shapes.

`RaftDataStateMachine::before_open_target` cleans stale `.REMOVE` trash, detects Init/Migrating/Completed states from marker and data-directory contents, writes a synced `MIGRATING-RAFT` marker when a dump is needed, and removes inconsistent partial target/source data during recovery. `after_dump_data` keeps target data, removes source data, and removes the marker with directory syncs.

## State And Persistence
Most typed config wrappers are value-only and persist through serde/TOML or `online_config::ConfigValue`. `ReadableSizeOrPercent` loses percentage intent after parsing because it stores only resolved bytes. `VersionTrack` state is in-memory and lock/atomic protected.

Persistent effects include directory creation, fd limit changes, Linux `/proc` and mount inspection, data-dir file counts, log-path canonicalization, and Raft migration marker/data-directory mutation. The Raft state machine explicitly syncs marker files and parent directories and renames directories through `.REMOVE` trash before deletion to support crash recovery.

## Dependencies And Integration
Depends on `serde`, `serde_json`, `thiserror`, `chrono`, `online_config`, `url`, `libc`, `lazy_static`, TiKV `time`, `sys::SysQuota`, and logging macros. The module is consumed by TiKV server config loading, online config updates, logger setup, storage engine directory validation, and Raft engine migration paths.

## Risks
Percentage size parsing depends on runtime memory quota and serializes as absolute bytes, so re-emitting config can obscure the original operator intent. `parse_string_to_vec` unwraps JSON parsing and can panic on invalid schedule strings before returning its own error. Several filesystem helpers and the Raft state machine use `unwrap`/`assert` because they run during startup or migration and treat unexpected states as fatal. `TomlWriter` is not a general TOML rewriter and can mishandle quoted keys, inline tables, or multi-line values. The tracker version/value update is not atomic, so false positives are possible as documented.

## Test Signals
Tests cover size parsing/serde including scientific notation and invalid units, percentage sizes, duration construction/parsing, offset time and schedule matching, path canonicalization, Linux kernel/data-dir helpers, address validation, file-count and empty-dir checks, multi-tracker updates, TOML rewriting and empty-content insertion, and many Raft migration/recovery states including partial marker writes and nested target paths.
