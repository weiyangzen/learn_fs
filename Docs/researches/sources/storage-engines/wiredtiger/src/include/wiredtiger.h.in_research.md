# Research: sources/storage-engines/wiredtiger/src/include/wiredtiger.h.in

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-008984`: lines 1-5046, `Docs/researches/chunks/subset-b-008984_research.md`
- `subset-b-008985`: lines 5047-10412, `Docs/researches/chunks/subset-b-008985_research.md`

## Chunk Research

### subset-b-008984: lines 1-5046

# sources/storage-engines/wiredtiger/src/include/wiredtiger.h.in lines 1-5046

## Chunk Scope

This chunk is the first half of WiredTiger's generated public C API template. The researched span is `sources/storage-engines/wiredtiger/src/include/wiredtiger.h.in:1-5046`, from the header guard and version macros through the beginning of the `WT_FILE_SYSTEM` extension interface. The later half of the same source file continues the custom file-handle, storage-source, page-log, statistics, and verbose-category definitions.

The file is a `.h.in` template: version macros are substituted during the build, and large sections are generated from WiredTiger's API metadata scripts (`dist/api_data.py`, `dist/api_err.py`, and flag-generation tooling). It is the ABI-facing contract for applications, language bindings, examples, and extensions.

## Purpose

This header defines the primary WiredTiger API surface:

- Core opaque handles: `WT_CONNECTION`, `WT_SESSION`, `WT_CURSOR`, `WT_ITEM`, and `WT_MODIFY`.
- Database lifecycle APIs: `wiredtiger_open`, `wiredtiger_strerror`, `wiredtiger_version`, and error-log dump helpers.
- Cursor CRUD, positioning, range bounds, and cursor state rules.
- Session-level schema, logging, verification, transaction, checkpoint, and timestamp APIs.
- Connection-level configuration, session creation, global timestamp, rollback-to-stable, extension-registration, page-log/storage-source, encryption-key-provider, and diagnostics APIs.
- Utility APIs for packing/unpacking, config parsing, checksums, and delta-modify calculation.
- Public error and sub-level error code constants.
- Initial extension interfaces: event handlers, collators, compressors, custom data sources, encryptors, and file-system flags/typing.

The header is intentionally documentation-heavy. It is both an include file and the source of Doxygen-generated API docs, so behavioral requirements are embedded in comments as part of the public contract.

## Important APIs, Types, and Functions

### Template and visibility infrastructure

- `WIREDTIGER_VERSION_MAJOR`, `WIREDTIGER_VERSION_MINOR`, `WIREDTIGER_VERSION_PATCH`, and `WIREDTIGER_VERSION_STRING` are build-substituted placeholders.
- `WT_ATTRIBUTE_LIBRARY_VISIBLE` marks public symbols with default ELF visibility under GCC/Clang when the library is otherwise built with hidden visibility.
- `__F(func)` abstracts function-pointer declaration syntax for normal C builds versus Doxygen/SWIG documentation generation.
- The include set is intentionally small and stable: POSIX/C integer, varargs, boolean, and stdio types.

### Data representation

- `WT_ITEM` is the raw byte-buffer carrier used by cursors, packing APIs, config APIs, and extension callbacks. Public fields are `data` and `size`; internal builds also expose managed-memory bookkeeping and the `WT_ITEM_INUSE` flag.
- `WT_MODIFY` describes byte-range modifications for `WT_CURSOR::modify` and `wiredtiger_calc_modify`: new bytes, target offset, and replace length. Offsets beyond the current value pad with spaces for `S` values and NULs for raw `u` values.
- `WT_INTPACK64_MAXSIZE` and `WT_INTPACK32_MAXSIZE` define upper bounds for packed integer encodings used by struct packing and internal record-number buffers.

### Cursor API

`WT_CURSOR` is the main record access handle. The public members expose its owning `WT_SESSION`, `uri`, `key_format`, and `value_format`, then a table of method pointers:

- Data access: `get_key`, `get_value`, `get_raw_key_value`, `set_key`, and `set_value`.
- Positioning: `compare`, `equals`, `next`, `prev`, `reset`, `search`, and `search_near`.
- Modification: `insert`, `modify`, `update`, `remove`, and `reserve`.
- Lifecycle and metadata: `checkpoint_id` for checkpoint cursors, `close`, `largest_key`, `reconfigure`, and `bound`.

Cursor behavior is stateful. `set_key` and `set_value` stage inputs for the next operation and save packing errors so the later API call fails cleanly. Cursor-returned `WT_ITEM` memory is valid only until the next cursor operation. Successful search/update/modify/reserve operations may leave the cursor positioned and holding resources, while insert and some remove paths leave it unpositioned. `reset` releases those resources and invalidates current key/position state.

The internal protected cursor fields in this span show integration points for cursor caching (`cache`, `reopen`, `WT_CURSTD_CACHEABLE`, `WT_CURSTD_CACHED`), URI hashing, session cursor queues, record-number storage, JSON/language binding private data, raw key/value buffers, saved errors, internal URIs, lower/upper bound buffers, and many standard cursor flags. The flags encode append, bulk, dump formats, history-store cursor behavior, metadata ownership, overwrite/raw/key-only modes, bound inclusivity, and key/value ownership.

### Session API

`WT_SESSION` encapsulates thread-local and transactional context. Its public API includes:

- Lifecycle and configuration: `close`, `reconfigure`, `strerror`, `reset`, and `get_last_error`.
- Cursor handles: `open_cursor`, with support for table/file/statistics/backup/config/custom data-source cursors, cursor duplication, checkpoint cursors, raw/dump/readonly modes, next-random cursors, incremental backup cursors, and per-cursor statistics selection.
- Schema and object operations: `alter`, `bind_configuration`, `create`, `compact`, `drop`, `publish`, `salvage`, `truncate`, and `verify`.
- Logging: `log_flush` and `log_printf`.
- Transactions: `begin_transaction`, `commit_transaction`, `prepare_transaction`, and `rollback_transaction`.
- Transaction timestamps and prepared IDs: `query_timestamp`, `timestamp_transaction`, `timestamp_transaction_uint`, `prepared_id_transaction`, and `prepared_id_transaction_uint`.
- Checkpoint and visibility support: `checkpoint`, `reset_snapshot`, and `transaction_pinned_range`.
- Internal/debug entry point: `breakpoint`.

Key schema configuration in `create` spans allocation/page sizing, compressors, block manager selection, checksums, column groups, collators, column names, dictionaries, disaggregated storage, encryption, import/repair, key/value formats, overflow thresholds, per-object logging, memory page limits, OS cache controls, prefix compression, split percentage, tiered storage, object type, and timestamp usage assertions. `alter` exposes a smaller post-create subset. `drop`, `salvage`, `truncate`, and `verify` are exclusive or non-transactional where documented, and failures may force active transactions to roll back.

Transaction methods document the API-level control flow: begin creates a transaction context; commit/rollback end it; prepare narrows allowed follow-up operations to commit or rollback. Timestamp APIs require snapshot isolation and enforce ordering against oldest/stable timestamps, prepare timestamps, durable timestamps, and optional preserve-prepared semantics. Numeric timestamp/prepared-id variants avoid hex-string parsing costs.

### Connection API

`WT_CONNECTION` is process/shared connection state. Methods in this chunk include:

- `close`, with shutdown checkpoint controls.
- `debug_info` for invasive diagnostic dumps by subsystem.
- `reconfigure`, for runtime cache, eviction, logging, statistics, tiered-storage, verbose, diagnostics, load-control, operation-tracking, and rollback-to-stable tuning.
- `get_home`, `compile_configuration`, `configure_method`, and `is_new`.
- `open_session`, inheriting session defaults such as cursor caching, cache wait behavior, isolation, prefetch, and session debug flags.
- Global timestamp APIs: `query_timestamp`, `set_timestamp`, and `rollback_to_stable`.
- Extension registration: `load_extension`, `add_data_source`, `add_collator`, `add_compressor`, `add_encryptor`, and `set_file_system`.
- Non-Doxygen/internal extension hooks: `add_page_log`, `add_storage_source`, `get_page_log`, `get_storage_source`, `set_context_uint`, `dump_error_log`, `set_key_provider`, and `get_key_provider`.
- `get_extension_api`, which exposes the extension helper function table defined later in the file.

`WT_CONTEXT_TYPE_LAST_MATERIALIZED_LSN` appears in this span as a disaggregated/page-log integration context value.

### Database open and support functions

- `wiredtiger_open` opens or creates a WiredTiger home, installs an event handler, applies environment/config-file ordering rules, loads early extensions, and returns a `WT_CONNECTION`.
- `wiredtiger_strerror` provides a process-global string form for return codes; `WT_SESSION::strerror` is the thread-safe variant.
- `wiredtiger_dump_error_log` exposes the diagnostic error-log buffer without a connection event handler.
- `wiredtiger_struct_pack`, `wiredtiger_struct_size`, and `wiredtiger_struct_unpack` implement one-shot binary format packing.
- Streaming pack/unpack uses `WT_PACK_STREAM` plus `wiredtiger_pack_start`, `wiredtiger_unpack_start`, `wiredtiger_pack_close`, `wiredtiger_pack_item`, `wiredtiger_pack_int`, `wiredtiger_pack_str`, `wiredtiger_pack_uint`, and matching unpack calls.
- Config parsing uses `WT_CONFIG_ITEM`, `wiredtiger_config_validate`, `wiredtiger_config_parser_open`, and `WT_CONFIG_PARSER::{next,get}`. `WT_CONFIG_ITEM` preserves non-NUL-terminated string spans, numeric interpretation, and item type (`STRING`, `BOOL`, `ID`, `NUM`, `STRUCT`).
- Checksum helpers return cacheable function pointers for CRC32C with and without a starting seed.
- `wiredtiger_calc_modify` derives a bounded set of `WT_MODIFY` records from old/new values, returning failure if the approximate diff cannot fit within caller limits.
- `wiredtiger_version` returns runtime library version numbers and string.

### Error constants

The generated error section reserves WiredTiger-specific codes in the `-31800` range. Public codes in this chunk include `WT_ROLLBACK`, `WT_DUPLICATE_KEY`, `WT_ERROR`, `WT_NOTFOUND`, `WT_PANIC`, internal `WT_RESTART`, `WT_RUN_RECOVERY`, `WT_CACHE_FULL`, `WT_PREPARE_CONFLICT`, and `WT_TRY_SALVAGE`. `WT_DEADLOCK` aliases `WT_ROLLBACK` for backward compatibility.

Sub-level errors use the `-32000` range to refine top-level failures. This span includes `WT_NONE`, cache overflow, write conflict, oldest-for-eviction, backup/data-handle/schema/table/checkpoint conflicts, uncommitted/dirty data blockers, modify visibility limits under read-uncommitted, live-restore conflicts, and disaggregated-storage conflicts. `WT_SESSION::get_last_error` is the public access path for the last top-level error, sub-level error, and message.

### Event and extension interfaces

- `WT_EVENT_HANDLER` defines callbacks for errors, messages, progress, automatic handle close, and general typed events. General event types include compact-check iterations, connection close/ready, and application-thread eviction participation.
- `WT_COLLATOR` provides `compare`, optional per-data-source `customize`, and `terminate`.
- `WT_COMPRESSOR` provides mandatory `compress`/`decompress`, optional `pre_size`, and `terminate`.
- `WT_DATA_SOURCE` lets extensions own URI schemes and implement `alter`, `create`, `compact`, `drop`, `open_cursor`, `rename`, `salvage`, `size`, `truncate`, `range_truncate`, `verify`, `checkpoint`, and `terminate`.
- `WT_ENCRYPTOR` provides mandatory `encrypt`, `decrypt`, and `sizing`, optional key-aware `customize`, and `terminate`.
- `WT_FS_OPEN_FILE_TYPE` and file-system flags begin the custom file-system API. Flags in this span describe random/sequential access hints, create/durable/exclusive/read-only opens, fixed/internal paths, forced mmap, and durable remove/rename.

## Control Flow and Behavioral Contracts

### Opening and configuring a database

The top-level flow is `wiredtiger_open` -> `WT_CONNECTION::open_session` -> `WT_SESSION::create/open_cursor` -> `WT_CURSOR` operations. Configuration can be supplied through environment variables, home-directory config files, and explicit strings. The header documents both initial `wiredtiger_open` settings and runtime `WT_CONNECTION::reconfigure`/`WT_SESSION::reconfigure` controls, so generated config metadata is a central dependency.

`compile_configuration` and `bind_configuration` add an optimized path for repeated API calls where config parsing is expensive. The binding contract is explicit: bound strings are not copied, so callers must maintain their lifetime while used.

### Cursor lifecycle and data operations

Cursor use is staged:

1. `WT_SESSION::open_cursor` opens by URI or duplicates another cursor.
2. Applications set keys/values or move/search the cursor.
3. Data methods read, insert, modify, update, remove, or reserve records.
4. `reset` drops position/resources; `close` releases the handle or may put it in the session cursor cache.

The cursor API comments encode important postconditions: inserts generally end without a cursor position, `WT_DUPLICATE_KEY` may leave an existing value readable, update/modify/reserve leave the cursor positioned, and checkpoint/statistics cursors have special reset semantics. Cursor bounds are configured by setting a key and calling `bound` for lower/upper inclusive or exclusive ranges.

### Schema and maintenance operations

Schema operations are non-transactional or exclusive where marked. `create` materializes metadata and storage objects; `alter` modifies selected settings; `drop`, `rename` through data sources, `truncate`, `compact`, `salvage`, and `verify` interact with data handles and filesystem blocks. Some failures force active transactions to roll back because schema state and transactional data could otherwise diverge.

`truncate` is explicitly scan-and-write rather than range-locked, so concurrent inserts/updates in or near the range have weaker conflict guarantees. `salvage` rebuilds files in place and can make deleted records reappear or inserted records disappear. These details are part of the public correctness contract.

### Transaction and timestamp flow

The transaction state machine is session-scoped:

1. `begin_transaction` starts an active transaction with isolation, read timestamp, prepare-handling, priority, sync, and timeout settings.
2. Cursor operations operate inside that transaction until it ends.
3. Optional `timestamp_transaction`/`timestamp_transaction_uint` set read, commit, durable, prepare, or rollback timestamps under snapshot-isolation rules.
4. Optional `prepare_transaction` records prepare state and then permits only commit or rollback.
5. `commit_transaction` or `rollback_transaction` resolves the transaction and resets cursors on rollback or failed commit.

Global timestamp flow is connection-scoped. `set_timestamp` advances oldest, stable, stable disaggregated schema epoch, or durable timestamp bounds. `query_timestamp` reports derived values such as all-durable, pinned, oldest reader, checkpoint/recovery timestamps, and disaggregated schema epochs. `rollback_to_stable` discards timestamped updates newer than the global stable timestamp in checkpoint-durable tables and requires applications to stop concurrent API activity.

### Checkpoint and persistence flow

`WT_SESSION::checkpoint` creates a transactionally consistent database or object snapshot. With timestamps and `use_timestamp=true`, checkpoint-durable tables exclude updates newer than the stable timestamp, while commit-durable/logged tables include committed updates. Checkpoints serialize with each other, can be named or dropped, and can trigger tiered-storage flushes.

Connection close may create a final checkpoint, controlled by `skip_checkpoint` and `use_timestamp`. `wiredtiger_open` recovery, logging configuration, rollback-to-stable, and salvage define the restart-time persistence behavior exposed in this half of the header.

### Extension dispatch flow

Applications register extension implementations on the connection, usually during extension initialization. WiredTiger later dispatches into registered function tables:

- Custom data-source callbacks implement URI-specific schema and cursor operations.
- Custom collators participate in key comparison and can be customized per URI/config.
- Compressors and encryptors sit in block/log/object write and read paths.
- Event handlers receive diagnostics, progress, and lifecycle events.
- The custom file-system interface starts in this chunk and is completed later in the file.

The comments repeatedly state whether callbacks may be invoked concurrently and whether `terminate` is the final access to the handle.

## State and Persistence Behavior

The API surface separates several kinds of state:

- Connection state: home directory, global configuration, extensions, global timestamps, cache/eviction/logging/statistics subsystems, file-system hooks, diagnostic state, and global rollback-to-stable context.
- Session state: default isolation, cursor cache, active transaction, transaction timestamps/prepared ID, app-private pointer, last error/sub-error/message, prefetch/debug/cache-wait settings, and pinned transaction range.
- Cursor state: URI, formats, key/value buffers, current position, saved packing errors, range bounds, raw/dump/overwrite/append/cache flags, language binding storage, and internal key/value ownership.
- Persistent database state: metadata entries, btree files, checkpoints, logs, history store, tiered objects, imported/exported files, encryption metadata, and optional disaggregated page-log/schema-epoch state.

Durability is configurable per connection and object. Logging provides commit-level durability when enabled; objects can set `log=(enabled=false)` for checkpoint-level durability. Checkpoint behavior is timestamp-aware, and rollback-to-stable reconciles persistent content to stable timestamp rules. In-memory databases bypass normal disk persistence and may return `WT_CACHE_FULL` for writes that exceed configured cache.

The extension APIs can also own persistent state: data sources manage their own URI-backed objects; compressors/encryptors transform stored blocks; file-system implementations mediate file creation/removal/rename durability; storage-source/page-log hooks integrate tiered and disaggregated storage.

## Dependencies and Integration Points

- Build scripts substitute version placeholders and generate configuration/error/flag sections. Manual edits in generated blocks are fragile.
- Doxygen and SWIG conditionals shape both public documentation and language-binding exposure. For example, some internal fields and APIs are hidden from bindings, and `app_private` is not exposed to non-C bindings.
- POSIX/C errno-style return values coexist with WiredTiger-specific negative error constants.
- `WT_SESSION::create`, `WT_CONNECTION::reconfigure`, and `wiredtiger_open` depend on the generated config grammar and validation tables.
- Examples referenced through `@snippet` are integration signals for docs and API usage.
- Compression, encryption, custom data sources, collators, custom file systems, page logs, storage sources, and key providers are extension registration points anchored by this header.
- Timestamp APIs integrate with transaction visibility, checkpoint, history store, rollback-to-stable, backup checkpoint pinning, and disaggregated schema epochs.
- Backup/incremental backup behavior appears through cursor configuration, checkpoint drop restrictions, and backup cursor truncation semantics.
- Debug/diagnostic options integrate with diagnostic builds, verbose categories, event handlers, and internal crash/rollback injection paths.

## Risks and Edge Cases

- ABI compatibility risk is high: handle layout and function-pointer order are public for C clients and extensions.
- Generated blocks must stay synchronized with generator scripts; editing generated config/error/flag text directly can produce inconsistent docs, parser tables, and symbols.
- Varargs APIs (`get_key`, `set_key`, packing, timestamp/config binding) cannot validate C argument types at compile time; callers must match the declared formats exactly.
- Cursor-owned memory lifetimes are short. Holding `WT_ITEM::data` across cursor operations is unsafe unless copied.
- Transaction timestamp ordering is strict and differs for prepared versus non-prepared transactions. Misordered commit/durable/prepare/read/rollback timestamps return errors and can force transaction rollback.
- `rollback_to_stable` requires quiescing transactions/cursors/API calls. Calling it concurrently with normal workload violates the documented contract.
- Range truncate does not provide range locks, so concurrent range modifications can produce ambiguous conflict or recovery outcomes.
- `salvage=true` and `WT_SESSION::salvage` are destructive recovery tools and can lose or resurrect records.
- Event-handler and extension callback return codes are not always ignored; non-zero callback returns can fail user operations or the library.
- Compression/encryption callbacks must respect buffer sizing contracts. A bad `pre_size` or `sizing` implementation risks overruns, failed reads, or unreadable persisted blocks.
- Encryptor key customization can create per-key encryptor instances whose lifecycle must be terminated correctly.
- Custom data-source and file-system implementations must be thread-safe because WiredTiger may call them from multiple threads.
- `bind_configuration` does not duplicate strings, making caller-owned string lifetime part of correctness.
- Debug options such as rollback injection, checkpoint crash points, log retention, diagnostic asserts, and cursor copy/reposition can intentionally change control flow or crash behavior.

## Test Signals

Useful validation for changes touching this span includes:

- Build the generated header and ensure `wiredtiger.h` has no placeholder leakage, duplicate constants, malformed flag values, or Doxygen/SWIG syntax regressions.
- Run API smoke tests that open a database, open/close sessions and cursors, perform insert/search/update/remove/modify, and validate cursor postconditions after reset/close/reconfigure/bound.
- Run transaction tests covering snapshot isolation, commit/rollback failure reset behavior, prepare/commit/durable timestamp ordering, rollback timestamps under preserve-prepared, numeric timestamp APIs, and `WT_PREPARE_CONFLICT`.
- Run checkpoint, close-checkpoint, rollback-to-stable, recovery, log flush, and timestamp-global tests to verify persistence semantics.
- Run schema tests for create/alter/drop/compact/truncate/salvage/verify, including exclusive/EBUSY cases and non-transactional failure rollback behavior.
- Run config parser and config validation tests for `wiredtiger_open`, `WT_CONNECTION::reconfigure`, `WT_SESSION::create`, `WT_SESSION::open_cursor`, and compiled/bound configurations.
- Run packing/unpacking tests for one-shot and streaming APIs, including raw items, strings, signed/unsigned integers, buffer-size errors, and `WT_INTPACK*_MAXSIZE` bounds.
- Run extension tests for custom collators, compressors, encryptors, data sources, file systems, event handlers, and `get_extension_api`.
- Run error-reporting tests for `wiredtiger_strerror`, `WT_SESSION::strerror`, `WT_SESSION::get_last_error`, top-level WiredTiger errors, sub-level errors, and diagnostic error-log dump APIs.
- Run docs generation and example snippet checks because this header doubles as the source of public documentation.

### subset-b-008985: lines 5047-10412

# sources/storage-engines/wiredtiger/src/include/wiredtiger.h.in lines 5047-10412

Chunk: `subset-b-008985`

This chunk covers the second half of WiredTiger's public/generated API header template. It starts inside the `WT_FILE_SYSTEM` interface and then defines the file-handle, storage-source, page-log, key-provider, extension-entry, public constant, statistics-key, and verbose logging portions of `wiredtiger.h.in`. The file is an API contract rather than implementation code: the control flow is expressed as callback tables, stable numeric constants, and generated statistic identifiers that are consumed by WiredTiger core code, extensions, applications, and test tooling.

## Purpose

The chunk's main purpose is to publish ABI-facing contracts for storage and observability features:

- Custom file systems and file handles, including directory listing, object existence, open/remove/rename/size/free-space, mmap-style access, pread/pwrite, durable sync, truncate, file extension, and advisory calls.
- Non-public storage-source and page-log interfaces used by tiered/disaggregated storage, shared object storage, page logging, block cache, and checkpoint materialization.
- Key-provider hooks for encrypted checkpoint key rotation and persistence acknowledgement.
- Extension entry points (`wiredtiger_extension_init` and optional `wiredtiger_extension_terminate`).
- Stable constants for incremental backup result types, live restore state, and transaction log record/operation types.
- A generated statistic reference exposing 1,436 statistic keys: 1,019 connection keys, 406 data-source keys, and 11 session keys.
- Verbose category and verbosity-level enums used by diagnostic logging configuration.

Because this is a generated/template header, many values are part of external contracts. Comments explicitly warn that log operation values, page-log flag values, and the generated statistics section must not be casually edited or renumbered.

## Important APIs, Types, and Constants

### `WT_FILE_SYSTEM` tail and `WT_FILE_HANDLE`

The chunk begins with the tail of `struct __wt_file_system`, so the structure definition and earlier methods are in the previous chunk. Visible methods include:

- `fs_directory_list` and internal `fs_directory_list_single`: allocate arrays of path strings for directory/prefix scans.
- `fs_directory_list_free`: releases the directory-list allocation.
- `fs_exist`: probes object existence.
- `fs_open_file`: opens a `WT_FILE_HANDLE` and requires the file-system implementation to allocate the handle and its `name`.
- `fs_remove` and `fs_rename`: optional for read-only file systems and accept durable flags.
- `fs_size` and `fs_free_space`: report object size and free bytes.
- `terminate`: optional cleanup callback after WiredTiger will no longer access the file system.

`struct __wt_file_handle` is the per-file vtable returned by `fs_open_file`. It stores its owning `WT_FILE_SYSTEM *file_system` and allocated `char *name`, then exposes callbacks for:

- lifecycle: `close`;
- access hints: `fh_advise` with `WT_FILE_HANDLE_WILLNEED` and `WT_FILE_HANDLE_DONTNEED`;
- allocation and truncation: `fh_extend`, `fh_extend_nolock`, `fh_truncate`;
- interprocess locking: `fh_lock`;
- mapping: `fh_map`, `fh_map_discard`, `fh_map_preload`, `fh_unmap`;
- I/O and durability: `fh_read`, `fh_write`, `fh_size`, `fh_sync`, `fh_sync_nowait`.

Most methods may be `NULL` when unsupported, but core read/write/size/close behavior is foundational for storage engines. Thread-safety comments say WiredTiger may call most file-handle methods concurrently; extension implementers own synchronization. `fh_extend` and `fh_truncate` are documented as serialized per handle, while `fh_extend_nolock` is the opt-in concurrent extension hook.

### `WT_STORAGE_SOURCE`

The non-Doxygen `struct __wt_storage_source` is an application-provided storage-source interface registered through `WT_CONNECTION::add_storage_source`. It models object-store buckets as customized `WT_FILE_SYSTEM` instances:

- `ss_add_reference` and `terminate` implement reference management. `WT_CONNECTION::get_storage_source` adds references, and `terminate` releases them.
- `ss_customize_file_system` binds a bucket name, auth token, and optional `cache_directory` config to a returned file system. Objects created through that file system are not visible until their handle closes and are immutable after creation.
- `ss_flush` copies a default-file-system file into an object name in shared storage.
- `ss_flush_finish` renames the source file into the local cache after a flush.

The storage-source contract is tightly coupled to tiered storage and object storage semantics. Local `WT_FILE_HANDLE::fh_sync` only syncs the local cached file and does not imply remote object transfer; remote transfer is handled by storage-source flush methods.

### Page Log and Disaggregated Storage

The chunk defines page-log constants, service interfaces, argument structs, and handle methods behind `#if !defined(DOXYGEN)`:

- `WT_PAGE_LOG_LSN_MAX` is `UINT64_MAX`, used as a maximum/latest LSN sentinel.
- `WT_DISAGG_START_LSN` is `1 << 32`, used by server step-up to avoid eviction of pages before a materialization point.
- `struct __wt_page_log` provides callbacks for reference management, checkpoint abandon/complete/query, testing-only last-LSN hooks, open-checkpoint query, per-table handle open, last-materialized LSN update, table trim, and termination.
- `struct __wt_page_log_handle` provides per-table page operations: `plh_put`, `plh_get`, `plh_get_page_ids`, `plh_discard`, `plh_close`, and block-cache helpers `plh_cache_put`, `plh_cache_has`, `plh_cache_del`, `plh_cache_available`.

Associated argument structs encode page-log state:

- `WT_PAGE_LOG_COMPLETE_CHECKPOINT_ARGS`: checkpoint id, checkpoint timestamp, checkpoint metadata, oldest timestamp, and output LSN.
- `WT_PAGE_LOG_GET_COMPLETE_CHECKPOINT_ARGS`: completed checkpoint LSN/id/timestamp/metadata.
- `WT_PAGE_LOG_PUT_ARGS`: backlink/base LSNs, backlink/base checkpoint ids, image size, stable flags, output LSN, and block-cache delta count.
- `WT_PAGE_LOG_GET_ARGS`: optional requested LSN, flags, returned backlink/base state, and delta count.
- `WT_PAGE_LOG_DISCARD_ARGS`: backlink/base state plus currently-unused flags and output LSN.

Page-log flags `WT_PAGE_LOG_COMPRESSED`, `WT_PAGE_LOG_DELTA`, `WT_PAGE_LOG_ENCRYPTED`, and `WT_PAGE_LOG_COLD` are documented as externally consumed and potentially persisted, so their numeric values must remain stable. `WT_BTREE_STORAGE_TIER` currently distinguishes no tier from cold tier, and the page-log flag range reserves values for storage tiers.

### Encryption Key Provider

`struct __wt_crypt_keys` stores encrypted key material plus a timestamp and a union result field: checkpoint LSN on success or an error code on failure. `struct __wt_key_provider` exposes:

- `load_key`: load the current persisted key during checkpoint load.
- `get_key`: fetch the latest key for checkpoint writes. WiredTiger may call once with an empty `keys` item to learn required size, then allocate and call again for data. Implementations must keep the key stable across those calls within one checkpoint.
- `on_key_update`: notify whether a key has been persisted, with LSN or error in `WT_CRYPT_KEYS::r`.
- `set_key`: hand WiredTiger a future checkpoint key associated with a timestamp. The timestamp must exceed both the global stable timestamp and any previous `set_key` timestamp. The call is explicitly non-transactional.
- `terminate`: cleanup when the provider is no longer accessed.

This interface creates a persistence boundary between checkpoint state, encrypted key blobs, stable timestamp rules, and external key-management modules.

### Extension Entrypoints and Public Constants

Extensions must export `wiredtiger_extension_init(WT_CONNECTION *, WT_CONFIG_ARG *)`, called by `WT_CONNECTION::load_extension`. They may export `wiredtiger_extension_terminate(WT_CONNECTION *)`, called during connection close.

The chunk also defines stable macro constants for:

- Incremental backup item types: invalid, whole file, file range.
- Live restore states: init, in progress, complete.
- Transaction log record and operation types: checkpoint, commit, file sync, message, system records; column/row put/remove/truncate/modify operations; checkpoint start; previous LSN; diagnostic timestamp operation; backup id. The comments say these values are written into the log and must never change except by appending new values.

### Statistics Reference

The statistics block is generated by `dist/stat.py` and marked `DO NOT EDIT`. It defines integer keys for `statistics:` cursors:

- Connection statistics start at `WT_STAT_CONN_AUTOCOMMIT_READONLY_RETRY = 1000` and run through `WT_STAT_CONN_TXN_UPDATE_CONFLICT = 2018`.
- Data-source statistics start at `WT_STAT_DSRC_AUTOCOMMIT_READONLY_RETRY = 2000` and run through `WT_STAT_DSRC_TXN_UPDATE_CONFLICT = 2405`.
- Session statistics start at `WT_STAT_SESSION_BYTES_READ = 4000` and run through `WT_STAT_SESSION_CACHE_TIME_MANDATORY = 4010`.

Major metric families include autocommit, background compaction, backup and incremental backup, block cache, disaggregated block manager, block manager, btree shape, cache and eviction, capacity throttling, checkpoint and checkpoint cleanup, compression, connection resources, cursor operations and cursor bounds, data-handle sweep, disaggregated role/checkpoint pickup, layered table manager, live restore, load control, locks, log manager, performance histograms, prefetch, reconciliation/page deltas/time windows, session schema operations, thread state/yield waits, tiered storage, and transactions/rollback-to-stable/timestamps.

The statistic macros are not behavior themselves; they are numeric API keys. Their correctness depends on exact alignment with generated metadata and runtime statistic tables. Duplicate-looking concepts intentionally appear at both connection and data-source scopes with different key ranges.

### Verbose Logging

`WT_VERBOSE_CATEGORY` enumerates diagnostic categories such as API, backup, block manager, checkpoint, disaggregated storage, eviction, extension, file operations, history store, layered, live restore, log, metadata, page delta, prefetch, reconcile, recovery, rollback-to-stable, tiered, timestamp, transaction, verify, and write. The enum is bracketed by `VERBOSE ENUM START/STOP`, suggesting generation or tooling rewrites the category list.

`WT_VERBOSE_LEVEL` is severity/verbosity ordered from `WT_VERBOSE_ERROR = -3` through warning, notice, info, and `WT_VERBOSE_DEBUG_1` to `WT_VERBOSE_DEBUG_5`.

## Control Flow and Call Sequences

This header does not execute code directly, but it defines expected call sequences:

- File-system lifecycle: WiredTiger gets a `WT_FILE_SYSTEM`, calls directory/object/open methods, receives allocated `WT_FILE_HANDLE` objects, performs file-handle I/O/mapping/sync/truncate operations, then calls handle `close` and eventually file-system `terminate`.
- Storage-source lifecycle: the connection registers or retrieves a storage source, references it, customizes bucket-backed file systems, writes local immutable objects, flushes them to shared storage, optionally finishes by moving the local source into cache, then terminates references.
- Page-log lifecycle: the connection registers/retrieves a page log, opens per-table handles, writes page images or deltas with checkpoint/page ids, reads by checkpoint and optional LSN, lists live page ids, discards entries, trims tables, completes or abandons checkpoints, and closes handles/services.
- Key-provider lifecycle: checkpoint load calls `load_key`, checkpoint write calls `get_key` possibly twice for size/data, persistence completion calls `on_key_update`, administrative key rotation calls `set_key`, and connection shutdown calls `terminate`.
- Statistics access: applications open statistics cursors and use these macros as keys. Runtime values are populated elsewhere; this header only binds names to numeric IDs.
- Verbose logging: applications configure categories and levels by enum values; logging sites elsewhere classify events using the same enum.

## State and Persistence Behavior

Several definitions in this chunk describe durable or externally visible state:

- File-system durability flows through `WT_FS_DURABLE` flags on remove/rename and through `fh_sync`/`fh_sync_nowait` on file handles. A custom file system that weakens these semantics can break checkpoint, log, and metadata durability.
- Storage-source objects become visible only after the creating handle closes and are immutable once created. Remote object transfer is separate from local file sync and is represented by `ss_flush`/`ss_flush_finish`.
- Page-log LSNs, checkpoint ids, checkpoint timestamps, backlink/base LSNs, and page flags encode disaggregated storage history. The header explicitly treats page-log flags as stable persisted/external values.
- `WT_DISAGG_START_LSN` is a cross-component server coordination sentinel for step-up/materialization behavior.
- Encrypted checkpoint keys carry timestamps and persisted LSN/error results. `set_key` is non-transactional and constrained by stable timestamp ordering.
- Log record and operation macro values are persisted in transaction logs and must not be renumbered.
- Statistic key values are public cursor keys. Renumbering breaks clients, tests, and tooling that refer to `WT_STAT_*` constants.

## Dependencies and Integration Points

The chunk depends on earlier declarations from the same header: `WT_CONNECTION`, `WT_SESSION`, `WT_CONFIG_ARG`, `WT_ITEM`, `WT_FILE_SYSTEM`, `WT_FILE_HANDLE`, `WT_STORAGE_SOURCE`, `WT_PAGE_LOG`, `WT_KEY_PROVIDER`, `WT_PAGE_LOG_HANDLE`, `WT_FS_OPEN_FILE_TYPE`, and `wt_off_t`.

Runtime integration points include:

- POSIX-like filesystem semantics: fadvise, mmap/madvise/munmap, pread/pwrite, sync, truncate, locking, durable rename/remove behavior.
- Extension loading via exported C symbols.
- Storage-source registration through connection APIs and object-store-backed file-system customization.
- Disaggregated storage/page-log consumers, checkpoint code, block cache, materialization frontier handling, layered tables, and server step-up behavior.
- Encryption/key-management modules that need checkpoint-aligned key persistence.
- Statistics cursors (`statistics:` URI family) and generated stats tooling (`dist/stat.py`).
- Verbose logging configuration and generated verbose category tooling.

## Risks and Edge Cases

- ABI and persisted-value drift: changing log operation values, page-log flags, statistic IDs, or enum ordering can break persistent data, external modules, or application binaries.
- Concurrency bugs in custom implementations: the header repeatedly states WiredTiger may call callbacks concurrently, while reentrancy is not expected for page-log interfaces. Implementers must guard shared state without assuming serialized entry.
- Memory ownership mismatches: `fs_directory_list`, `fs_open_file`, page-log `plh_get`, and key-provider `get_key` all carry allocation/ownership rules. Leaks, double frees, or returning stack-backed buffers would fail under normal core cleanup.
- Durability semantic gaps: `fh_sync_nowait`, `fh_sync`, durable remove/rename flags, and storage-source flush semantics are separate. Treating local cache sync as remote object persistence is explicitly wrong.
- Immutable object semantics: storage-source files opened with create should not be visible before close and cannot later be opened for mutation. Violating that contract can expose partial objects or corrupt tiered-storage assumptions.
- Page-log result ambiguity: `plh_get` says zero results must be associated with an error code. Returning success with no result would make callers unable to distinguish not-found, corruption, and empty data.
- Key rotation races: `get_key` must be stable between size and data fetch within a checkpoint; `set_key` must obey timestamp ordering and is non-transactional, so caller-side transaction rollback will not undo it.
- Generated-section edits: the stats block is built by tooling. Manual edits are likely to be overwritten or leave runtime tables out of sync.

## Test Signals

Useful test signals for code touching this chunk or its generators:

- API/header generation tests should verify `dist/stat.py` output matches the generated statistics block and that no manual changes are needed.
- ABI/persistence guards should detect renumbering of `WT_LOGREC_*`, `WT_LOGOP_*`, `WT_PAGE_LOG_*` flags, `WT_STAT_*` IDs, and verbose categories where external configuration depends on ordering.
- Custom file-system tests should exercise directory-list allocation/free, read/write/size, durable sync, truncate/extend, read-only `NULL` methods, exclusive open error paths, and concurrent calls.
- Storage-source tests should verify object invisibility before close, immutability after creation, bucket/prefix naming edge cases, cache-directory configuration, flush/finish ordering, and reference-count termination.
- Page-log/disaggregated tests should cover put/get/discard/checkpoint-complete/checkpoint-query/table-trim, live page-id listing, cache helper behavior, zero-result error handling, compressed/delta/encrypted/cold flags, and materialization-frontier LSN behavior.
- Key-provider tests should cover two-pass `get_key`, unchanged-key size zero, within-checkpoint key stability, `on_key_update` success/error reporting, timestamp validation against stable timestamp and previous keys, and non-transactional `set_key` behavior.
- Statistics cursor tests should confirm representative connection, data-source, and session statistics keys resolve to expected names/values, especially for newer disaggregated, layered, live-restore, page-delta, and rollback-to-stable metrics.
- Verbose tests should confirm configured categories and levels map to the intended runtime output and that `WT_VERBOSE_ERROR` remains the most critical level.

## Cross-Chunk Notes

This chunk begins mid-definition of `WT_FILE_SYSTEM`; earlier methods and type declarations are outside the assigned range. It also contains callback declarations whose implementations live in WiredTiger core, extension modules, storage-source implementations, page-log providers, and generated stats/verbose tooling. The final per-file research report should merge this with earlier chunks to describe the whole `wiredtiger.h.in` API surface coherently.
