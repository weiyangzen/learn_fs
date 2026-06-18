# sources/test-tools/kdevops/scripts/kconfig/menu.c

## Purpose
`menu.c` builds, finalizes, traverses, validates, and describes the in-memory Kconfig menu tree. It receives parse-time events from `parser.y`, attaches properties to symbols, propagates dependencies, creates automatic submenus, flattens promptless containers, validates symbol properties, and formats extended help/search relationship text used by `mconf` and `nconf`.

## Important APIs, Types, And Functions
Core exports include `_menu_init()`, `menu_add_entry()`, `menu_add_menu()`, `menu_end_menu()`, `menu_add_dep()`, `menu_set_type()`, `menu_add_prompt()`, `menu_add_visibility()`, `menu_add_expr()`, `menu_add_symbol()`, `menu_finalize()`, `menu_next()`, `menu_is_visible()`, `menu_is_empty()`, `menu_get_prompt()`, `menu_get_parent_menu()`, `get_relations_str()`, and `menu_get_ext_help()`. Important globals are `rootmenu`, `current_menu`, `current_entry`, `last_entry_ptr`, and the weak `get_jump_key_char()` hook overridden by menu UIs.

## Control Flow
During parsing, `menu_add_entry()` appends a new `struct menu` under `current_menu`, `menu_add_menu()` descends into the current entry, and `menu_end_menu()` returns to the parent. Properties are appended to the owning symbol and current menu node. `menu_finalize()` recursively calls `_menu_finalize()`, which rewrites `m` dependencies through `MODULES`, applies parent dependencies to child menus and property visibility, records reverse dependencies for `select` and `imply`, creates automatic submenus for consecutive dependent nodes, flattens invisible/promptless containers, and validates type/default/select/range consistency. Runtime helpers evaluate prompt visibility and build relation/help text.

## State And Persistence
The file mutates the global menu tree and symbol property lists in memory. No disk persistence occurs directly, but finalized dependencies drive later `.config`, autoconf, search, and UI behavior. Search result jump keys allocate `struct jump_key` entries into a caller-provided list; callers own cleanup.

## Dependencies And Integration Points
`parser.y` is the primary producer of calls into this file. `symbol.c` consumes finalized dependencies and visibility. UI frontends consume `menu_is_visible()`, `menu_get_prompt()`, `menu_get_ext_help()`, and `get_relations_str()`. It depends on expression helpers (`expr_*`), symbols (`sym_*`), linked lists, hashtable-backed symbols indirectly, and `xalloc`.

## Risks And Edge Cases
Dependency propagation uses copied expressions in places to avoid shared-expression mutation; regressions here can silently alter Kconfig semantics. Automatic submenu creation is subtle and can restructure the tree based on expression superset checks. Property validation is warning-oriented for many cases, so invalid Kconfig may proceed. The local source shows a duplicated nested `prop_warn(prop,` fragment in `sym_check_prop()`, which appears syntactically suspicious and should be verified by compilation or upstream comparison.

## Test Signals
Test with Kconfig snippets covering nested `menu`, `if`, `visible if`, `depends on m`, duplicate types/prompts, ranges, `select`, `imply`, choice defaults, promptless symbols, automatic submenu creation, and search/help output. Build tests should catch the apparent duplicated `prop_warn` artifact.
