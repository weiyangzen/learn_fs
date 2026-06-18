# Research: sources/storage-engines/wiredtiger/src/config/config_def.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-008969`: lines 1-4049, `Docs/researches/chunks/subset-b-008969_research.md`
- `subset-b-008970`: lines 4050-4830, `Docs/researches/chunks/subset-b-008970_research.md`

## Chunk Research

### subset-b-008969: lines 1-4049

# sources/storage-engines/wiredtiger/src/config/config_def.c lines 1-4049

## Chunk Scope

This chunk is the generated front portion of WiredTiger's main configuration definition file. The file starts with `DO NOT EDIT: automatically built by dist/api_config.py`, includes `wt_internal.h`, defines shared choice-string constants, and then emits `WT_CONFIG_CHECK` arrays plus per-array jump tables for public API methods, metadata records, and several `wiredtiger_open` variants.

The researched span is `sources/storage-engines/wiredtiger/src/config/config_def.c:1-4049`. It ends in the middle of `confchk_wiredtiger_open_usercfg`; the `config_entries` registry and helper functions such as `__wt_conn_config_init`, `__wt_conn_config_discard`, and `__wt_conn_config_match` are later in the same generated file and are outside this chunk.

## Purpose

The chunk provides the static schema that WiredTiger uses to validate configuration strings. Each `WT_CONFIG_CHECK` row describes one legal key: its name, textual type, optional validation callback, textual constraints, nested subconfiguration table, compiled type enum, generated key id, integer min/max bounds, and legal choice set. The matching jump table narrows key lookup by first character before binary search.

The generated data covers:

- Connection APIs: `WT_CONNECTION.close`, `debug_info`, `load_extension`, `open_session`, `query_timestamp`, `reconfigure`, `rollback_to_stable`, `set_key_provider`, and `set_timestamp`.
- Cursor APIs: `WT_CURSOR.bound` and `WT_CURSOR.reconfigure`.
- Session APIs: alter, begin/commit/rollback/prepare/timestamp transactions, checkpoint, compact, create, drop, log flush, open cursor, publish, query timestamp, salvage, and verify.
- Metadata schemas: `colgroup_meta`, `file_config`, `file_meta`, `index_meta`, `layered_meta`, `object_meta`, `table_meta`, `tier_meta`, and `tiered_meta`.
- Open-time connection schemas: reusable subconfig tables and the main `wiredtiger_open`, `wiredtiger_open_all`, `wiredtiger_open_basecfg`, and partial `wiredtiger_open_usercfg` definitions.

## Important APIs, Types, and Data Structures

`WT_CONFIG_CHECK` is the central type. In `src/include/config.h`, it contains `name`, `type`, `checkf`, `checks`, `subconfigs`, `subconfigs_entries`, `subconfigs_jump`, `compiled_type`, `key_id`, `min_value`, `max_value`, and `choices`. The tables in this chunk populate those fields directly.

`WT_CONFIG_COMPILED_TYPE_*` values encode runtime type expectations:

- `BOOLEAN` accepts boolean values or numeric 0/1.
- `CATEGORY` recursively validates a nested key/value struct using `subconfigs`.
- `FORMAT` is used for format strings such as `key_format` and `value_format`; these rows call `__wt_struct_confchk`.
- `INT` enforces numeric type and optional min/max bounds.
- `LIST` expects a structured/list value when non-empty and may restrict members through `choices`.
- `STRING` accepts any config value as string-like text, with optional choice checks.

Choice constants such as `__WT_CONFIG_CHOICE_snapshot`, `__WT_CONFIG_CHOICE_all`, `__WT_CONFIG_CHOICE_recovery`, `__WT_CONFIG_CHOICE_data`, and `__WT_CONFIG_CHOICE_log` are emitted once and reused through `confchk_*_choices` arrays. This gives validation and compiled configuration code stable pointer identities for common values, including boolean normalization in the compilation path.

Jump tables have type `uint8_t[WT_CONFIG_JUMP_TABLE_SIZE]`. They map ASCII first characters to the start/end offsets in a sorted `WT_CONFIG_CHECK` array. Runtime validation uses these offsets to restrict `bsearch` to the relevant contiguous slice instead of searching the full table.

## Configuration Families

### Connection and Session APIs

The first part defines compact method-level schemas. Examples include:

- `confchk_WT_CONNECTION_close` with `debug.skip_checkpoint`, `final_flush`, `leak_memory`, and `use_timestamp`.
- `confchk_WT_CONNECTION_open_session` and `confchk_WT_SESSION_reconfigure`, which share cursor-cache, cache wait, debug, isolation, and prefetch options.
- `confchk_WT_CONNECTION_reconfigure`, a large runtime-reconfiguration schema for cache, checkpointing, debug mode, disaggregated storage, eviction, logging, statistics, tiered storage, timing stress, and verbose controls.
- Transaction tables for begin, commit, rollback, prepare, timestamp, and prepared-id APIs. These validate timestamp strings, isolation choices, ignore-prepare modes, sync options, operation timeouts, priorities, and prepared transaction identifiers.
- `confchk_WT_SESSION_open_cursor`, which validates cursor behavior flags, checkpoint reads, debug dump-version controls, incremental backup cursor options, dump formats, raw mode, read-only mode, targets, and statistics choices.

### Creation and Metadata Schemas

`confchk_WT_SESSION_create` defines create-time schema for object layout and storage behavior: allocation sizes, access pattern hints, block allocation/manager/compressor, cache residency, checksums, column/key/value formats, encryption, disaggregated options, import, LSM, page sizes, prefix compression, tiered storage, and timestamp usage policy.

The metadata tables mirror or extend create-time schemas for persisted metadata records:

- `confchk_colgroup_meta` and `confchk_table_meta` validate high-level table/column-group metadata.
- `confchk_file_config` is a create-like file configuration schema.
- `confchk_file_meta`, `confchk_object_meta`, `confchk_tier_meta`, and `confchk_tiered_meta` include persisted checkpoint, object id, live-restore, flush timestamp/time, readonly/tiered object markers, version, tier lists, and tier cache/bucket fields.
- `confchk_index_meta` adds index-specific `extractor`, `immutable`, and format fields.
- `confchk_layered_meta` includes disaggregated and stable-layer metadata fields.

These tables are important because they validate metadata strings loaded from WiredTiger metadata, not only user-supplied API configuration.

### Open-Time Schemas

The `wiredtiger_open` portion builds many reusable subconfig tables before the main open schemas. Notable nested groups include:

- `block_cache`: enablement, cache-on-write/checkpoint behavior, NVRAM path, cache sizing, hash sizing, overhead, and type.
- `checkpoint` and `checkpoint_cleanup`: periodic checkpoint timing, log-size threshold, cleanup method, file wait, and wait interval.
- `debug_mode`: crash injection, corruption abort behavior, checkpoint/log retention, eviction and cursor stress toggles, page history, realloc behavior, rollback error, tiered flush behavior, and disaggregated address-cookie upgrade controls.
- `disaggregated`: role, checkpoint metadata, drain threads, local file action, page log, last materialized LSN, and destructive reset acknowledgment.
- `eviction`, `file_manager`, `heuristic_controls`, `history_store`, `io_capacity`, `load_control`, `operation_tracking`, `page_delta`, `rollback_to_stable`, `shared_cache`, `statistics_log`, `tiered_storage`, `transaction_sync`, and `prefetch`.
- `chunk_cache`, including capacity, chunk size, hash size, storage type choices (`FILE` or `DRAM`), and insertion/eviction controls.
- `compatibility`, `encryption`, `hash`, `live_restore`, and `log`.

`confchk_wiredtiger_open` includes administrative and environment flags such as `backup_restore_target`, `buffer_alignment`, `builtin_extension_config`, `compile_configuration_count`, `config_base`, `create`, `direct_io`, `extensions`, `file_extend`, `hazard_max`, `in_memory`, `mmap`, `multiprocess`, `precise_checkpoint`, `preserve_prepared`, `readonly`, `salvage`, session sizing, environment usage, `verify_metadata`, and `write_through`.

`confchk_wiredtiger_open_all`, `confchk_wiredtiger_open_basecfg`, and `confchk_wiredtiger_open_usercfg` are close variants that differ in which keys are legal for all/open-base/user configuration contexts. In this chunk, `wiredtiger_open_usercfg` is visible through `page_delta` at line 4049; its remaining keys continue after the chunk.

## Control Flow

This generated file does not execute control flow by itself. Its tables are consumed by validation and configuration compilation paths:

1. A caller obtains a `WT_CONFIG_ENTRY` for a method, usually through `WT_CONFIG_REF(session, name)` or by method-name lookup.
2. `__wt_config_check` receives the entry and config string. It skips work if there is no config/check array, or if the string is already recognized as compiled configuration.
3. `__config_check` parses each key/value pair, validates that the key token is an id/string, and searches the entry's `WT_CONFIG_CHECK` array.
4. `__config_check_search` uses the generated jump table and the first character of the key to bound a binary search over the sorted check array.
5. The selected row's `compiled_type` drives type validation. `CATEGORY` recurses into `subconfigs`; `LIST` and `STRING` may consult `choices`; `INT` checks numeric type and min/max bounds; `FORMAT` rows defer detailed structure validation through callbacks such as `__wt_struct_confchk`.
6. If a row has a validation callback or choice set, those checks run after basic type validation.

The configuration compilation path in `src/conf/conf_compile.c` also depends on the same rows. It uses compiled types to choose `WT_CONFIG_ITEM_TYPE`, normalizes boolean values to shared choice strings, binds placeholders for precompiled config strings, and invokes `__wt_conf_check_one` against row-level constraints.

## State and Persistence Behavior

The chunk contains static immutable data. It does not mutate connection, session, metadata, or file state directly.

Its persistence relevance comes from the schemas it defines:

- Metadata validation tables are applied to persisted metadata strings for files, objects, tables, tiers, tiered metadata, indexes, column groups, and layered/disaggregated records.
- Open-time options such as `config_base`, `compatibility`, `log`, `tiered_storage`, `disaggregated`, `live_restore`, and `encryption` determine how later connection setup reads or writes durable files and metadata.
- Generated `key_id` fields align with generated `WT_CONF_ID_*` identifiers in `conf_keys.h`; compiled configuration stores parsed values by these ids for fast access.

Because these tables are generated, the durable contract is the source data in `dist/api_data.py` plus generator behavior in `dist/api_config.py`. Manual edits to this file would be overwritten and risk desynchronizing `config_def.c`, `config.h` entry indices, and `conf_keys.h` ids.

## Dependencies and Integration Points

Direct compile-time dependencies in this chunk include:

- `wt_internal.h`, which brings in `WT_CONFIG_CHECK`, `WT_CONFIG_ENTRY`, `WT_CONFIG_COMPILED_TYPE_*`, size macros such as `WT_KILOBYTE` and `WT_TERABYTE`, and validation callbacks.
- `__wt_struct_confchk`, referenced by format keys.
- Generated config ids and entry indices from `src/include/conf_keys.h` and `src/include/config.h`.
- `WT_CONFIG_JUMP_TABLE_SIZE`, `INT64_MIN`, and `INT64_MAX` for jump table sizing and unconstrained bounds.

Runtime integration points include:

- `src/config/config_check.c` for API and metadata validation.
- `src/conf/conf_compile.c` for precompiled configuration parsing and binding.
- `src/config/config_api.c` for extension-provided configuration checks.
- Connection open/reconfigure code in `src/conn/conn_api.c`, which consumes keys validated by the `wiredtiger_open*` and connection reconfigure tables.
- Public API wrappers that call `__wt_config_check` through generated `WT_CONFIG_ENTRY_*` identifiers.

## Risks and Maintenance Notes

- The arrays must remain sorted by key name for jump-table-bounded binary search. Generator bugs or manual edits that break sorting can make valid keys fail validation.
- `subconfigs_entries` must match the number of non-sentinel rows in the referenced subconfig table. A mismatch can narrow searches incorrectly or expose rows from the wrong range.
- Choice arrays must stay synchronized with textual `choices=[...]` strings. The text is mostly documentary for diagnostics/generation, while runtime enforcement uses the `choices` pointer array.
- Min/max bounds use expanded unit macros such as `10LL * WT_TERABYTE`; overflow or inconsistent units would silently change accepted ranges.
- Reused `key_id` values allow common concepts such as `enabled`, `name`, `log`, `verbose`, and timestamp fields to compile consistently across APIs. Incorrect ids would affect compiled configuration lookup even when textual validation passes.
- The assigned chunk cuts off inside `confchk_wiredtiger_open_usercfg`, so research for final registry entries and config initialization/discard helpers must come from later chunks.

## Test Signals

Useful validation signals for this chunk are broad configuration tests rather than unit tests of individual rows:

- API tests that pass invalid keys, wrong types, out-of-range integers, and invalid choice values through public methods should fail with `EINVAL`.
- Metadata tests that load or create table/file/index/object/tiered metadata exercise the metadata tables.
- Connection tests using `wiredtiger_open` with `config_base`, `compatibility`, logging, backup/readonly, live-restore, disaggregated, tiered storage, encryption, cache sizing, and statistics options exercise the open schemas.
- Python suite references to `config_base=false`, compatibility releases, readonly opens, base configuration files, timestamp/log settings, and backup scenarios are especially relevant because those keys are validated here before deeper connection behavior runs.
- Generated-file consistency checks should rerun `dist/api_config.py` and verify no drift in `src/config/config_def.c`, `src/include/config.h`, and `src/include/conf_keys.h`.

### subset-b-008970: lines 4050-4830

# sources/storage-engines/wiredtiger/src/config/config_def.c - chunk subset-b-008970 research

Chunk scope: lines 4050-4830 of `sources/storage-engines/wiredtiger/src/config/config_def.c`. This is chunk 2 of 2 for `config_def.c`, an auto-generated WiredTiger configuration definition file built by `dist/api_config.py`.

## Purpose

This chunk completes the generated configuration metadata used by WiredTiger's configuration parser, validator, and optional compiled-configuration fast path. It covers the tail of `confchk_wiredtiger_open_usercfg`, the jump table for that check array, the full `config_entries[]` catalog for public/internal configuration methods, and the small runtime helpers that attach the static catalog to a connection.

The main role of the chunk is declarative rather than algorithmic: it maps method names such as `WT_SESSION.create`, metadata schemas such as `file.meta`, and connection-open variants such as `wiredtiger_open_usercfg` to default configuration strings, validation arrays, jump tables, stable method IDs, and precompiled configuration sizing metadata. Runtime code elsewhere uses this table to avoid hand-maintained per-method parsing rules.

## Important APIs, Types, and Functions

- `confchk_wiredtiger_open_usercfg` tail: lines 4050-4128 complete validation for user-visible `wiredtiger_open_usercfg` options. The visible keys include `precise_checkpoint`, `prefetch`, `preserve_prepared`, `readonly`, `rollback_to_stable`, `salvage`, `session_max`, `session_scratch_max`, `session_table_cache`, `shared_cache`, `statistics`, `statistics_log`, `tiered_storage`, `timing_stress_for_test`, `transaction_sync`, `verbose`, `verify_metadata`, and `write_through`. Category keys point to subconfig arrays defined earlier in the file, list keys point to generated choice arrays, and integer keys carry min/max bounds.
- `confchk_wiredtiger_open_usercfg_jump`: lines 4130-4135 define a 128-entry ASCII jump table. `WT_CONFIG_JUMP_TABLE_SIZE` is 128, and the lookup path uses the first key character to skip into sorted check arrays before binary search.
- `config_entries[]`: lines 4137-4784 define the static `WT_CONFIG_ENTRY` catalog. Each entry contains method/schema name, base/default configuration string, `WT_CONFIG_CHECK` array pointer, number of checks, check jump table, stable method ID, optional compiled-config sizing, and a boolean `compilable` flag.
- `__wt_conn_config_init(WT_SESSION_IMPL *session)`: lines 4786-4805 allocates `conn->config_entries` as an array of pointers, then copies pointers to every static `config_entries[]` element through the NULL terminator.
- `__wt_conn_config_discard(WT_SESSION_IMPL *session)`: lines 4807-4815 frees the per-connection pointer array allocated by init. It does not free the static entries themselves.
- `__wt_conn_config_match(const char *method)`: lines 4817-4830 linearly searches the static catalog and returns the matching entry by method string, or `NULL` if absent. This is a general lookup helper for callers that do not already have the generated numeric `WT_CONFIG_ENTRY_*` index.

The data types are declared in `src/include/config.h`: `WT_CONFIG_CHECK` describes a single key's type, range, choices, subconfigs, and compiled key ID; `WT_CONFIG_ENTRY` describes one method/configuration namespace. `WT_CONFIG_REF(session, n)` indexes `S2C(session)->config_entries` by generated `WT_CONFIG_ENTRY_*` constants. `WT_CONF_SIZING_INITIALIZE` and `WT_CONF_SIZING_NONE` come from `src/include/conf.h`; the former records stack/array sizes for APIs that support the compiled configuration path.

## Catalog Coverage

The `config_entries[]` table in this chunk covers several families:

- Connection API methods: extension registration, `WT_CONNECTION.close`, `debug_info`, `load_extension`, `open_session`, `query_timestamp`, `reconfigure`, `rollback_to_stable`, `set_key_provider`, and `set_timestamp`.
- Cursor/session API methods: cursor bound/reconfigure plus session alter, transaction, checkpoint, compact, create, drop, cursor-open, timestamp, salvage, truncate, verify, and related no-config methods.
- Metadata schema entries: `colgroup.meta`, `file.config`, `file.meta`, `index.meta`, `layered.meta`, `object.meta`, `table.meta`, `tier.meta`, and `tiered.meta`. These defaults mirror durable metadata fields such as checkpoint strings, live-restore state, tiered object state, object version, table/index formats, logging, encryption, disaggregated storage, and timestamp assertions.
- Connection-open variants: `wiredtiger_open`, `wiredtiger_open_all`, `wiredtiger_open_basecfg`, and `wiredtiger_open_usercfg`. These share many defaults but intentionally differ in fields such as `config_base`, `create`, `exclusive`, `in_memory`, `use_environment`, `use_environment_priv`, and `version` availability.

The stable method IDs in this table match the generated `WT_CONFIG_ENTRY_*` macros in `src/include/config.h`. This matters because callers on hot paths use numeric entries such as `WT_CONFIG_ENTRY_WT_SESSION_begin_transaction` rather than string search, and the compiled-configuration arrays in `src/conf/conf_compile.c` are parallel to this table.

## Control Flow

Generation flow is external to this C file: `dist/api_config.py` walks the API metadata, emits `WT_CONFIG_CHECK` arrays and jump tables, then writes `config_entries[]` sorted by method name with generated slot IDs. The same generator writes corresponding `WT_CONFIG_ENTRY_*` defines, so generated order must remain consistent across `config_def.c` and `config.h`.

Startup flow through this chunk is small but important. During connection initialization, `__wt_conn_config_init` allocates a per-connection pointer array sized to `WT_ELEMENTS(config_entries)`, assigns it to `conn->config_entries`, and fills it with pointers to the static entries including the NULL terminator. Later API paths use `WT_CONFIG_REF(session, name)` to resolve the entry for parsing, validation, and compiled default lookup.

Config validation flow is table-driven. Given a `WT_CONFIG_ENTRY`, the parser checks user strings against `entry->checks`, `entry->checks_entries`, and `entry->checks_jump`. Scalar entries validate type, min/max, and optional choices. Category entries recurse into their `subconfigs` arrays and subconfig jump tables. List entries validate tokens against choice arrays such as `confchk_verbose16_choices` and `confchk_timing_stress_for_test5_choices`.

Compiled configuration flow uses the same entry table. `src/conf/conf_compile.c` allocates `conn->conf_api_array` parallel to `conn->config_entries`, asserts `centry->method_id == i`, and precompiles default strings for entries marked `compilable`. In this chunk, `WT_CURSOR.bound`, `WT_SESSION.begin_transaction`, and `WT_SESSION.reconfigure` are explicitly marked compilable with sizing derived from their generated `WT_CONF_API_TYPE` layouts.

## State and Persistence Behavior

This chunk does not directly persist data, open files, or mutate on-disk metadata. Its persistent impact is indirect: the default strings and validation rules here define which configuration fields can be stored in WiredTiger metadata and which user-supplied connection/session strings are accepted at runtime.

The durable metadata-related entries are especially state-sensitive. `file.meta`, `object.meta`, `tier.meta`, and `tiered.meta` include checkpoint metadata, live-restore bitmap state, object/tier timestamps, tiered storage settings, version fields, readonly/tiered-object flags, and logging/encryption settings. Changes to these generated defaults or validation arrays can affect metadata compatibility and recovery behavior even though this chunk itself is static data.

In-memory state is limited to `WT_CONNECTION_IMPL.config_entries`: a connection-owned array of pointers into static read-only metadata. Allocation failure in `__wt_conn_config_init` returns through `WT_RET`. Cleanup is a single `__wt_free` call in `__wt_conn_config_discard`.

## Dependencies and Integration Points

- `wt_internal.h` pulls in the internal declarations for `WT_SESSION_IMPL`, `WT_CONNECTION_IMPL`, `WT_CONFIG_ENTRY`, `WT_CONFIG_CHECK`, memory helpers, and macros such as `S2C`, `WT_RET`, `WT_ELEMENTS`, and `__wt_free`.
- `src/include/config.h` defines `WT_CONFIG_CHECK`, `WT_CONFIG_ENTRY`, `WT_CONFIG_JUMP_TABLE_SIZE`, compiled type constants, `WT_CONFIG_REF`, and generated `WT_CONFIG_ENTRY_*` indexes.
- `src/include/conf.h` defines compiled-configuration sizing macros used by selected entries.
- `src/conf/conf_compile.c` consumes `conn->config_entries`, `method_id`, `compilable`, and sizing fields to build parallel compiled-default arrays.
- Parser/checking code in the `src/conf` area consumes check arrays, jump tables, choice arrays, min/max bounds, and category subconfigs for runtime validation.
- Public and internal API implementations use the generated method indexes to fetch base strings and check metadata for each API call.
- `dist/api_config.py` is the authoritative generator. Manual edits to this C file would be overwritten and are explicitly discouraged by the file header.

## Risks and Edge Cases

- Generated table/order drift is high impact. If `config_entries[]` order, `method_id`, generated `WT_CONFIG_ENTRY_*` macros, or compiled config arrays become inconsistent, direct indexed lookup can return the wrong configuration schema. `conf_compile.c` asserts `centry->method_id == i`, but non-compiled paths also rely on the same ordering contract.
- Default strings and check arrays must stay semantically aligned. A default key present in an entry's base string but missing from its check array, or vice versa, can cause startup validation failures or allow unsupported fields.
- Open-configuration variants are deliberately similar but not identical. Accidentally adding a field to `wiredtiger_open`, `wiredtiger_open_all`, `wiredtiger_open_basecfg`, or `wiredtiger_open_usercfg` without preserving their intended differences can expose internal-only settings to users or hide needed base settings.
- The jump tables assume 7-bit ASCII key names and sorted check arrays. Any generator bug that violates ordering or key-character assumptions degrades lookup correctness.
- `__wt_conn_config_match` is linear over the static catalog. That is acceptable for infrequent string-name lookup, but hot API paths should use generated numeric indexes through `WT_CONFIG_REF`.
- `__wt_conn_config_init` allocates an array including the NULL terminator. Consumers that iterate until `method == NULL` depend on that terminator being copied.
- Several entries govern test/failpoint-style options such as `timing_stress_for_test`, crash points, and debug modes. Incorrect validation choices can silently remove test coverage hooks or expose unintended diagnostic behavior.
- Metadata entries include compatibility-sensitive fields such as format versions, tiered metadata, checkpoint LSNs, live-restore fields, and disaggregated state. Generator changes require compatibility review, not just compile success.

## Test Signals

There are no direct unit tests inside this generated C file. Relevant test and validation signals are indirect:

- Regeneration checks should run the WiredTiger dist/generation workflow and verify that `config_def.c` and `src/include/config.h` remain synchronized with `dist/api_config.py` output.
- Build/compile coverage catches missing symbols for choice arrays, subconfig arrays, jump tables, and `WT_CONF_SIZING_INITIALIZE` types.
- Configuration parser tests exercise accepted/rejected strings through `WT_CONFIG_CHECK` metadata, especially category recursion and list choices for verbose/statistics/timing stress options.
- Connection startup tests exercise `__wt_conn_config_init` allocation and later cleanup through normal open/close flows.
- Compiled configuration tests should cover entries marked `compilable`, because those depend on the sizing fields and the parallel `method_id` indexing contract.
- Metadata compatibility and recovery tests are the primary signal for changes to `file.meta`, `object.meta`, `tier.meta`, and `tiered.meta` defaults.

## Cross-Chunk Notes

Chunk 1 contains the bulk of the generated `WT_CONFIG_CHECK` arrays and choice lists referenced here. The final per-file merge should connect those earlier validation definitions to this chunk's catalog entries, because this chunk is where all per-method schemas become reachable through `config_entries[]` and connection initialization.
