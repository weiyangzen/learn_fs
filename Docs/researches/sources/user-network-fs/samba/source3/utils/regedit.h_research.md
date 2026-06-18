<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/regedit.h -->
# sources/user-network-fs/samba/source3/utils/regedit.h

## Purpose

`regedit.h` declares the registry wrapper API and shared search/UI constants used by the Samba registry editor implementation.

## Important APIs, Types, and Functions

It declares `struct samba3_registry_key` as a wrapper around `struct registry_key *`, wrapper functions for opening hives/keys, enumerating values and subkeys, creating/deleting keys, deleting/setting/querying values, querying key metadata, initializing the registry, and opening a Samba3 registry context. It also declares `regedit_getch()`, `regedit_search_match_fn_t`, `struct regedit_search_opts`, and color-pair constants.

## Control Flow

The header has no runtime flow. `regedit.c` uses `reg_open_samba3()` to acquire a registry context and `regedit_dialog.c`/other UI modules call `regedit_getch()` for resize-aware input.

## State and Persistence Behavior

The wrapper functions declared here can mutate persistent registry state via create/delete/set operations. `regedit_search_opts` persists the active query and flags while the editor is running.

## Dependencies and Integration Points

It couples the curses UI modules to the Samba registry backend and wrapper implementation files such as `regedit_wrap.c` and `regedit_samba3.c`. It forward-declares registry and security types to limit include weight.

## Risks and Edge Cases

The API mixes read-only wrappers and mutating wrappers in one header, so consumers must be careful about which functions persist changes. `regedit_search_opts.query` ownership is managed by dialog code and can be replaced during searches. The wrapper type hides only one pointer, so backend abstraction is intentionally thin.

## Test Signals

Compile coverage across `regedit.c`, dialog, tree, value-list, wrapper, and Samba3 backend files validates declarations. Integration tests should verify each wrapper maps correctly to registry operations and that search options survive repeated search dialogs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/regedit.h -->
