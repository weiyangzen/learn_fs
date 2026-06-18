# sources/storage-engines/wiredtiger/src/cursor/cur_metadata.c

## Purpose
Implements the WiredTiger `metadata:` cursor family. It exposes metadata as a cursor over the metadata btree while also virtualizing the metadata table's own schema entry, which lives in the turtle file rather than as an ordinary metadata-table row. The `metadata:create` variant additionally strips internal-only schema details into a configuration suitable for `WT_SESSION.create`.

## Important APIs, types, and functions
The public entry point is `__wt_curmetadata_open`, which allocates `WT_CURSOR_METADATA`, installs metadata cursor methods, opens an underlying metadata file cursor, and optionally opens a second cursor for create-only config expansion. `WT_MD_CURSOR_NEEDKEY` and `WT_MD_CURSOR_NEEDVALUE` synchronize the public cursor buffers into the backing file cursor before delegated operations. `__schema_source_config` follows a `source=` URI in a metadata config and returns that source object's metadata. `__schema_create_collapse` removes non-create options and merges implicit column-group/source config for simple tables, named column groups, indices, and tiered shared-table column groups. `__curmetadata_setkv` copies a backing row into the public cursor, applying create-only collapse when required.

## Control flow
Opening sets key/value formats to `S`, then opens a metadata btree cursor via `__wt_metadata_cursor_open`; `metadata:create` sets `WT_MDC_CREATEONLY` and gets a second metadata cursor for source lookups. `next` starts at the synthetic metadata-table row if unpositioned, then scans the backing cursor at read-uncommitted isolation and skips incomplete entries. `prev` walks the backing cursor backwards and returns the synthetic metadata-table row when the backing scan reaches the beginning. `search` and `search_near` special-case keys matching `metadata:` or `file:WiredTiger.wt`; all other operations delegate to the backing cursor at read-uncommitted isolation. Inserts, updates, and removes call `__wt_metadata_insert`, `__wt_metadata_update`, and `__wt_metadata_remove` rather than directly mutating through the backing cursor.

## State, persistence, and dependencies
Cursor state is tracked with `WT_MDC_POSITIONED`, `WT_MDC_ONMETADATA`, and `WT_MDC_CREATEONLY`, plus standard cursor key/value flags. Persistent state is the WiredTiger metadata table and turtle-file metadata entry. The file depends on config parsing/collapse helpers, schema naming helpers, metadata cursor/search/update helpers, transaction-isolation macros, and the standard cursor initialization/close path.

## Integration points
This cursor is opened through `WT_SESSION.open_cursor` for `metadata:` and `metadata:create`; schema code uses it to inspect or copy object definitions. It integrates with the metadata subsystem instead of ordinary file cursor writes so metadata update semantics, locking, and turtle-file handling stay centralized.

## Risks and test signals
Risk centers on returning create-compatible configuration without leaking internal metadata, preserving read-uncommitted visibility for schema scans, and correctly ordering the synthetic metadata-table row relative to real rows. Tests should cover forward/reverse scans, search/search_near for both `metadata:` and `file:WiredTiger.wt`, readonly default behavior, write-enabled metadata cursors, implicit and tiered-shared column-group collapse, missing source entries, and incomplete metadata rows skipped during scans.
