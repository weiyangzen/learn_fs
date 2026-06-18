# sources/storage-engines/wiredtiger/test/cppsuite/src/main/database.cpp

Purpose: Implements the in-memory database/collection model and creates WiredTiger collections.

Important APIs/types/functions: `build_collection_name` returns `table:collection_<id>`. `add_collection` locks, validates create config, assigns an id, inserts a `collection`, creates the WT table, and records a schema operation if tracking is enabled. `add_existing_collections` seeds the model for reopened databases without creating tables. `get_collection`, `get_random_collection`, `get_collection_count`, `get_collection_names`, and `get_collection_ids` query model state. `set_timestamp_manager`, `set_operation_tracker`, and `set_create_config` wire dependencies and table config.

Control flow: collection creation is serialized by `_mtx`; random selection requires at least one collection. Compression, reverse collator, and disaggregated layered settings are appended to `DEFAULT_FRAMEWORK_SCHEMA`.

State and persistence: `_collections` and `_next_collection_id` track in-memory model state; `session->create` persists tables; operation tracker persists schema metadata with a timestamp.

Dependencies/integration: depends on `collection`, constants, random generator, scoped session, timestamp manager, operation tracker, and WT session API.

Risks and test signals: `add_collection` assumes timestamp manager is set when operation tracker is present. `get_random_collection` chooses ids from `0..count-1`, assuming collection ids are contiguous and never deleted from the model. `testutil_die/assert` catch missing config and invalid ids.
