# sources/storage-engines/wiredtiger/tools/gdb/gdb_scripts/wt_debug_script_update.py

## Purpose
`wt_debug_script_update.py` is an exploratory GDB Python script for dumping WiredTiger data handles, pages, insert lists, and update chains, including optional BSON decoding for MongoDB values. It predates the command-class style used by the other scripts and exposes helper functions directly in the GDB Python environment.

## Important APIs and functions
Important helpers include `dbg`, `walk_wt_list`, `get_data_handle`, `get_btree_handle`, `dump_update_chain`, `dump_insert_list`, `dump_skip_list`, `dump_modified`, `dump_disk`, `dump_leaf_page`, `dump_int_page`, and `dump_handle`. It initializes `conn_impl_ptr`, parses `session->iface->connection`, and dereferences it as a `WT_CONNECTION_IMPL`.

## Control flow and behavior
On import, the script prints/debugs type and connection information. Users call `get_data_handle(conn, handle_name, checkpoint_name)` to locate a handle in the connection's data-handle queue, then `dump_handle` to inspect the Btree root. Internal-page dumping recurses through page indexes; leaf-page dumping prints disk bytes and modified update/insert state. Update-chain dumping skips value reads for zero-size tombstone/reserve entries and attempts BSON decoding when type indicates a standard update.

## State, dependencies, and integration
The script depends on GDB Python, `bson`, WiredTiger debug types and field layout, and an in-scope `session` symbol in GDB. It is not imported by `load_gdb_scripts.py` in the current loader; it is likely sourced manually during deep debugging.

## Risks and test signals
Risks are high because the script executes work at import time, assumes `session` exists, uses broad `except` around BSON decoding, has hardcoded page/block header sizes, and contains older TODO/FIXME notes. Signals are successful handle discovery, readable root/internal/leaf page dumps, decoded BSON where applicable, and absence of GDB exceptions on known page structures.
