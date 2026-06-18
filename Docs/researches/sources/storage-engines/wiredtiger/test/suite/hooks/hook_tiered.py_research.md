<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/hooks/hook_tiered.py -->
# sources/storage-engines/wiredtiger/test/suite/hooks/hook_tiered.py

Purpose: Hook that runs ordinary row-store tests with tiered storage by injecting storage-source configuration, forcing tier flushes, adapting local-only creates, and skipping or stubbing unsupported tiered-table operations.

Important APIs and types: `wiredtiger_open_tiered`, helpers for readonly/failed/skipped test state, replacements for `Connection.close`, `Session.checkpoint`, `compact`, `create`, `open_cursor`, `salvage`, and `verify`, `TieredHookCreator`, argument parsing helpers, and `TieredPlatformAPI`.

Control flow: The open hook resolves the selected storage source from `helper_tiered`, rejects tests already using tiered/in-memory configs, creates the bucket directory, finds the extension, merges it into `extensions=[...]`, and appends `tiered_storage=(...)`. Checkpoint and close replacements force `flush_tier` unless readonly/failed/skipped. Create replacement marks non-table or column-store objects `tiered_storage=(name=none)`. Backup cursors and named checkpoints are skipped.

State and persistence behavior: Tests write both local WiredTiger state and tiered object files, with object names such as `<table>-0000000001.wtobj`. Platform API methods report tier-populate share/cache percentages, storage source name/config, and tiered filename existence. Dataset population uses those percentages to flush or reopen mid-fill.

Dependencies and integration points: Uses `helper_tiered.TieredConfigMixin`, `gen_tiered_storage_sources`, extension discovery, `WiredTigerTestCase` platform API delegation, and hook skip decorators.

Risks: Config parsing is regex/string based and handles only one level of parenthesized commas. Unsupported operations sometimes return success without doing work, so tests may pass with reduced semantic coverage. Object cleanup limitations make name-reuse tests problematic.

Test signals: Successful tiered runs show extension load, object creation, forced flush-tier checkpoints, correct `tableExists`/`initialFileName`, and expected skips for unsupported features.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/hooks/hook_tiered.py -->
