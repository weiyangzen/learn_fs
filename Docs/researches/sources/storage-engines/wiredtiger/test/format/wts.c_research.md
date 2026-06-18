# sources/storage-engines/wiredtiger/test/format/wts.c

Purpose: builds WiredTiger connection/table configuration for format, opens/closes databases, creates objects, handles event messages/progress, reopens connections, initializes precise checkpoint support, and writes statistics.

Important APIs and functions: `create_database`, `create_object`, `wts_create_home`, `wts_create_database`, `wts_open`, `wts_close`, `wts_reopen`, `wts_stats`, plus configuration helpers for encryption, timing stress, file manager, debug mode, eviction, live restore, disaggregated storage, tiered storage, prefetch, and obsolete cleanup.

Control flow: configuration helpers append settings into bounded buffers based on global/table config. `create_database` constructs a `wiredtiger_open` config with cache, statistics, in-memory/logging/encryption/block cache/checkpoint/timing/debug/disagg/tiered/prefetch/extensions/user overrides, then opens the connection. `create_object` builds per-table `WT_SESSION::create` config for key format, page sizes, compression, prefix compression, checksums, timestamps/logging, layered/disagg, and assertions. Open/close paths add nonpersistent options and optional metadata verification; stats opens statistics cursors and writes connection plus per-data-source stats.

State and persistence: creates/removes home directories, creates database/table files, updates `g.wts_conn` and `g.wts_conn_inmemory`, writes `OPERATIONS.stats`, opens extension libraries, and persists WiredTiger metadata/configuration. Precise checkpoint init sets stable timestamp before close after initial create.

Dependencies and integration: called by `t.c`, import, salvage, and reopen paths. It depends on `format_config`, `test_util` storage helpers, extension paths, event handler callbacks, trace connection state, disagg/tiered testutil builders, and global encryption keys.

Risks and test signals: config buffer exhaustion is fatal. Backward compatibility changes close behavior. In-memory mode uses one shared handle. Event handler routes verbose messages to trace or stdout and Antithesis-prefixed messages to stdout. Open failures include the generated home/config in diagnostics.
