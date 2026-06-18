# sources/storage-engines/wiredtiger/src/schema/schema_alter.c

Purpose: implements `WT_SESSION::alter` across files, tables, column groups, indexes, tiered trees, tiered objects, and tiered object ranges by rewriting metadata atomically under schema/checkpoint locks.

Important APIs and functions: `__wt_schema_alter` obtains an internal session and metadata tracking. `__schema_alter` dispatches by URI type. Core helpers include `__alter_apply`, `__alter_file`, `__alter_tier`, `__alter_object`, `__alter_tree`, `__alter_table`, `__alter_tiered`, `__alter_get_object_id_range`, and `__alter_objects`.

Control flow: metadata update starts with the relevant base metadata config, overlays existing metadata and user config, collapses the result, and updates only if changed. File and tier alteration use exclusive lock-only handle operations. Index and column-group alteration first alter their underlying data-source URI and then their own metadata. Table alteration with `exclusive_refreshed=true` opens the table exclusively, locks it in meta tracking, updates all column groups and indexes, then updates table metadata. Tiered alteration closes handles when exclusive, opens the tiered handle, alters local/shared tiers and all object metadata in the oldest-current id range, then updates tiered metadata.

State and persistence behavior: persistent state is the WiredTiger metadata table; handle locks are tracked so rollback can release or restore state on failure. The function can skip actual metadata writes when the collapsed configuration is unchanged and increments `session_table_alter_skip`.

Dependencies and integration points: depends on schema locks, checkpoint lock, metadata search/update, config collapse, handle-operation helpers, table/index/column-group open helpers, tiered naming, and meta tracking. It assumes callers already hold the necessary global schema/checkpoint serialization.

Risks: non-exclusive alter is allowed only for simple table metadata; applying it elsewhere would leave open handles with stale in-memory configuration. Recursive alteration of column-group/index sources must remain atomic with parent metadata. Tiered object ranges can be sparse, so missing object metadata is expected and must not abort. Any base-config omission can drop defaulted metadata fields during collapse.

Test signals: alter simple and complex tables, indexes, column groups, files, tiers, tiered trees with sparse object ranges, unchanged config skip stats, exclusive-refreshed rejection for unsupported URI types, and failure rollback through metadata tracking.
