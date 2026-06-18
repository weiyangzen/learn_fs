# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/show_deleted.c

Purpose: `show_deleted.c` implements the `show_deleted` LDB module, which hides deleted or recycled directory objects from normal searches and honors LDAP controls that request visibility of tombstones or recycled objects.

Important APIs, types, and functions: `struct show_deleted_state` caches whether recycle bin state needs refresh and whether it is enabled. `show_deleted_search()` rewrites search parse trees to exclude deleted/recycled entries when appropriate. `show_deleted_init()` registers `LDB_CONTROL_SHOW_DELETED_OID` and `LDB_CONTROL_SHOW_RECYCLED_OID` and initializes module state.

Control flow: Search requests for special DNs pass through unchanged. Without show-deleted or show-recycled controls, the module adds a `(!(isDeleted=TRUE))` filter. With controls present, it refreshes recycle-bin state if needed. If recycle bin is enabled and the caller did not request recycled objects, it excludes `isRecycled=TRUE`; otherwise it leaves the search tree unchanged. The rewritten search is issued as a child request and recognized controls are marked non-critical.

State and persistence behavior: The module has no durable state. It caches recycle-bin enabled status in module-private memory and refreshes lazily, tolerating missing feature objects during provisioning by assuming disabled. Query behavior is transient and expressed only by child search filters.

Dependencies and integration points: It depends on LDB parse trees, DSDB recycle-bin feature lookup, and LDAP show-deleted/show-recycled controls. Downstream modules execute the actual search. Rename and subtree modules use recycled visibility controls when they need internal access to deleted entries.

Risks: Incorrect filter rewriting can expose deleted/recycled objects or hide live ones. The recycle-bin state cache has a `need_refresh` guard to avoid recursion loops; moving that assignment could re-enter refresh logic. During provisioning, missing feature objects intentionally degrade to disabled behavior, which must remain compatible with startup order.

Test signals: Search tests should verify normal searches hide tombstones, show-deleted exposes deleted but not recycled objects when recycle bin is enabled, show-recycled exposes all states, and provisioning/startup without feature objects does not fail.
