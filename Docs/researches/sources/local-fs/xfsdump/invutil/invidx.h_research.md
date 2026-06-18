# File Research: sources/local-fs/xfsdump/invutil/invidx.h

Declares invutil inventory-index operations.

Key contents:
- Menu generation and file lifecycle: `generate_invidx_menu()`, `open_invidx()`, `close_invidx()`, `close_all_invidx()`, `remmap_invidx()`.
- Lookup helpers for matching stobj/invidx files and finding overlapping/insert positions.
- Raw stobj import helpers: `read_stobj_info()`, `insert_stobj_into_stobjfile()`, `insert_stobj_into_inventory()`.
- Menu operations: undelete, select, highlight, commit, prune.

Notable observations:
- Header exposes raw on-disk structs because invutil directly manipulates inventory files.
- `insert_stobj_into_inventory()` is declared here but not present in the read `invidx.c`, suggesting either stale declaration or implementation elsewhere/removed.
