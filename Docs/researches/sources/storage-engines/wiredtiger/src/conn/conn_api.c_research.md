# sources/storage-engines/wiredtiger/src/conn/conn_api.c

## Purpose

`conn_api.c` is the central implementation of the WiredTiger connection API. It binds the public `WT_CONNECTION` vtable, opens and closes database connections, configures connection-wide behavior, loads extensions, registers extension-provided components, manages early filesystem and encryption setup, coordinates startup and shutdown lifecycles, and exposes diagnostics, timestamps, sessions, and storage integrations.

## Important APIs, Types, and Functions

- Public entry point: `wiredtiger_open`.
- Public `WT_CONNECTION` method implementations: close, debug_info, reconfigure, get_home, compile_configuration, configure_method, is_new, open_session, query_timestamp, set_timestamp, rollback_to_stable, load_extension, add_data_source, add_collator, add_compressor, add_encryptor, set_file_system, add_page_log, add_storage_source, get_page_log, get_storage_source, set_context_uint, dump_error_log, set_key_provider, get_key_provider, and get_extension_api.
- Extension registries: `WT_NAMED_COLLATOR`, `WT_NAMED_COMPRESSOR`, `WT_NAMED_DATA_SOURCE`, `WT_NAMED_ENCRYPTOR`, `WT_KEYED_ENCRYPTOR`, `WT_NAMED_PAGE_LOG`, and `WT_NAMED_STORAGE_SOURCE`.
- Lifecycle helpers: `__wti_conn_ext_init`, `__wti_conn_ext_destroy`, `__wti_conn_backup_init`, `__wti_conn_backup_destroy`, `__conn_single`, `__conn_config_file_system`, `__conn_version_verify`, `__conn_startup_cleanup_and_verify`, and `__conn_write_base_config`.
- Config helpers: `__conn_config_file`, `__conn_config_env`, `__conn_hash_config`, `__conn_config_readonly`, `__conn_config_check_version`, `__wti_debug_mode_config`, `__wti_extra_diagnostics_config`, `__wt_verbose_config`, `__wti_timing_stress_config`, `__wti_json_config`, `__wti_heuristic_controls_config`, and `__wti_disagg_debug_mode_config`.

## Control Flow

`wiredtiger_open` initializes the library, allocates a `WT_CONNECTION_IMPL`, installs a static `WT_CONNECTION` method table, links the connection into the process list, and uses a dummy session until real sessions exist. It validates the application config, builds an initial config stack, determines early flags such as in-memory and read-only, sets the home directory, allocates hash tables, loads early extensions, configures the filesystem, verifies a clean startup directory, and claims exclusive ownership of the database home through process and file locking in `__conn_single`.

After that early phase, it builds the full config stack from defaults, compiled compatibility version, base config file, application config, user config file, environment config, and read-only overrides. It merges and stores the effective config, applies logging and diagnostics settings, sizes sessions, configures file extension and mmap behavior, handles prefetch and precise checkpoint compatibility, initializes compiled configuration and statistics, opens the real connection with `__wti_connection_open`, then loads non-early builtins and dynamic extensions. Encryption, logging compatibility, base config persistence, turtle and metadata initialization, optional metadata verification or salvage, prior metadata state, backup metadata, event notification, worker startup, recovery, startup cleanup, and final readiness flags follow in order.

`__conn_close` performs the reverse lifecycle carefully. It marks the connection no longer ready, rolls back active transactions, closes external sessions, temporarily sets minimal mode for final event handling and statistics, drains transaction activity, stops sweep, prefetch, live restore, background compact, checkpoint cleanup, checkpoint, and layered table manager services, runs transaction global shutdown and final checkpoint behavior, closes tiered storage with optional final flush, handles leak-memory configuration, records shutdown timing, and calls `__wti_connection_close`.

Registration methods allocate named wrapper objects and append them to connection queues under `api_lock` where needed. Removal methods walk queues, call terminate callbacks, release keyed or bucketed subobjects, and free wrapper memory. Configuration methods mostly parse named config entries and set connection flags or counters.

## State and Persistence Behavior

The file mutates nearly all connection-level state: home path, effective config string, extension queues, file system, key provider, encryption key cache, hash buckets, debug flags, verbose levels, timing stress flags, JSON output flags, cache cursor and checkpoint flags, prefetch settings, precise checkpoint and preserve prepared flags, read-only/in-memory/salvage flags, session array size, write-through settings, base configuration, compatibility versions, metadata state, backup state, readiness flags, and shutdown timing.

Persistent behavior includes reading `WiredTiger.basecfg`, `WiredTiger.config`, and `WIREDTIGER_CONFIG`; writing `WiredTiger.basecfg` through a temporary `WiredTiger.basecfg.set` file on database creation; creating and locking `WiredTiger.lock`; creating or validating the `WiredTiger` version file; initializing turtle and metadata files; optionally copying and salvaging metadata; dropping deprecated chunk cache metadata; and writing final checkpoint or tiered flush state during close.

## Dependencies and Integration Points

`conn_api.c` depends on broad WiredTiger internals: configuration parsing, OS filesystem adapters, dynamic loading, metadata, turtle files, schema operations, logging, recovery, timestamps, transaction management, checkpointing, eviction, sweep, prefetch, live restore, tiered/disaggregated storage, block cache, statistics, event handlers, call logging, and extension APIs. It integrates directly with generated config tables through `WT_CONFIG_BASE` and `WT_CONFIG_REF`, extension modules through `WT_CONNECTION` and `WT_EXTENSION_API`, and platform-specific filesystem implementations through `__wt_os_posix`, `__wt_os_win`, `__wt_os_inmemory`, and live restore filesystem setup.

## Risks and Edge Cases

- Startup order is fragile: early extensions must load before filesystem configuration, while encryption must wait until extensions have registered encryptors.
- Config stack precedence is central to correctness. Read-only overrides intentionally rewrite some settings, while other conflicts are rejected later.
- `__conn_single` mixes in-process checks, lock-file creation, byte locks, read-only exceptions, disaggregated mode, salvage behavior, and corruption detection; regressions can cause unsafe multi-process access or false startup failures.
- Extension registry operations rely on callback contracts. Missing encryptor callbacks, missing filesystem methods, or terminate/customize mismatches are validated in some paths but can still create cleanup complexity.
- Close ordering protects against races between sweep, sessions, checkpoints, transaction state, live restore, layered tables, and tiered storage; reordering can introduce use-after-free, leaked handles, or missed final checkpoints.
- Generated or persisted base configuration strips sensitive or run-specific fields. Incorrect filtering could persist secrets, persist nonportable runtime settings, or omit compatibility-critical settings.
- Error paths in `wiredtiger_open` must close partially initialized connections while preserving corruption signals such as `WT_TRY_SALVAGE`.

## Test Signals

High-value tests include open/close under normal, read-only, in-memory, salvage, exclusive, live restore, disaggregated, encrypted, and custom filesystem configurations; config precedence tests spanning application strings, base config files, user config files, and environment variables; extension registration and termination tests for collators, compressors, encryptors, data sources, page logs, storage sources, file systems, and key providers; lock-file and multi-process exclusion tests; metadata verify and salvage tests; final close ordering tests with active sessions and transactions; and failure-injection tests across partial startup to confirm cleanup, panic, and salvage-return behavior.
