# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/subtree_rename.c

Purpose: `subtree_rename.c` implements the `subtree_rename` LDB module. It expands a base rename into a subtree rename by moving immediate children under the new base DN, with recursion achieved by re-entering the same module for child renames.

Important APIs, types, and functions: `struct subtree_rename_context` tracks the original request and whether the base object has been renamed. `subren_ctx_init()` allocates context. `subtree_rename()` builds a one-level search under the old DN. `subtree_rename_search_onelevel_callback()` first renames the base, then rewrites and renames each child DN.

Control flow: Special DNs pass through. A normal rename performs a one-level search with `SHOW_RECYCLED` so internal moves can see deleted/recycled children. In the first callback invocation, before processing child entries, the module renames the base through the next module. For each child entry, it removes the old base components from the child DN, appends the new base DN, and calls `dsdb_module_rename()` with `DSDB_FLAG_OWN_MODULE`; that re-enters this module for grandchildren. When the search completes, the original request is completed successfully.

State and persistence behavior: There is no durable module state. Persistence is a sequence of downstream rename operations that moves the root before children. The context's `base_renamed` boolean prevents repeated base renames while the search yields child entries.

Dependencies and integration points: It uses LDB search/rename APIs, DSDB rename wrappers, recycled-object controls, and downstream constraint modules such as `samldb.c`, which checks rename policy before subtree movement. It assumes module-stack recursion will handle deeper descendants.

Risks: The root-first order means failures while moving descendants can leave partial movement unless the surrounding LDB transaction rolls back all operations. DN rewriting must preserve relative child paths exactly. Re-entry with `DSDB_FLAG_OWN_MODULE` is central to recursive behavior; changing flags could either skip grandchildren or loop incorrectly.

Test signals: Tests should rename leaf and multi-level subtrees, verify descendants preserve relative names, include deleted/recycled child visibility cases, and force a descendant constraint failure to confirm transaction rollback semantics.
