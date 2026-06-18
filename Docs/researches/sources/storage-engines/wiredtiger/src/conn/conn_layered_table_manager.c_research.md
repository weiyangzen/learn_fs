# sources/storage-engines/wiredtiger/src/conn/conn_layered_table_manager.c

## Purpose
This file manages the connection-level registry of currently open layered tables. The manager records stable, ingest, and layered URIs by ingest ID so other layered-table/disaggregated paths can discover open layered tables while handles are alive.

## Important APIs, Types, and Functions
The public functions are `__wti_layered_table_manager_init`, `__wt_layered_table_manager_add_table`, `__wt_layered_table_manager_remove_table`, and `__wti_layered_table_manager_destroy`. The local helper `__layered_table_manager_remove_table_inlock` removes one entry while the manager lock is held. Important types are `WT_LAYERED_TABLE_MANAGER`, `WT_LAYERED_TABLE_MANAGER_ENTRY`, and `WT_LAYERED_TABLE`.

## Control Flow and Behavior
Initialization asserts the manager is not already initialized, creates `layered_table_lock`, sizes the `entries` array to `conn->next_file_id + 1000` under the schema lock, sets `WT_CONN_SERVER_LAYERED`, and marks the manager initialized. Adding a table requires a layered dhandle context, allocates an entry, borrows URI pointers from the layered handle, grows the array if the ingest ID exceeds the current capacity, panics on duplicate registration, increments layered-table manager stats, and installs the entry under the spin lock. Removal is idempotent during shutdown: if initialized, it locks, frees the entry at the ingest ID, decrements stats, and clears the slot. Destroy clears the server flag, removes every remaining entry, frees the array, resets counters, marks the manager uninitialized, unlocks, and destroys the spin lock.

## State and Persistence
The manager is entirely in-memory. It does not persist table registrations; it relies on dhandle open/close lifecycle to add and remove entries. Entry URI strings are not copied, so their validity depends on the layered dhandle outliving the manager entry.

## Dependencies and Integration Points
This file integrates with data-handle open/close paths, layered table handles, connection server flags, schema locking for initial file-ID sizing, connection statistics, and verbose layered logging. `conn_open.c` destroys the manager after closing data handles, which matches the borrowed URI lifetime assumption.

## Risks
The main risks are incorrect ingest IDs causing array growth mistakes, duplicate opens overwriting manager entries, borrowed URI pointers surviving longer than the layered dhandle, and removal races around shutdown. The code assumes entries are protected by `layered_table_lock` and that removal after handle close is safe because checkpoints have already covered writes to the layered table.

## Test Signals
Test coverage should observe layered table open/close accounting, duplicate-open diagnostics, clean shutdown with open layered handles, and step-up/drain flows that depend on layered handles remaining discoverable while ingest tables need processing.
