# sources/user-network-fs/samba/source3/printing/printing_db.c

## Purpose

`printing_db.c` manages cached handles for per-printer print TDBs and stores the notification-subscriber PID list helper used by `printing.c`. It is a small persistence/cache layer around `tdb_open_log()` with reference counting and a maximum-open-DB recycling policy.

## Important APIs, Types, and Functions

- `get_print_db_byname()` finds or opens a `struct tdb_print_db` for a printer name, increments its refcount, and promotes it in an intrusive list.
- `release_print_db()` decrements the refcount and asserts it does not go negative.
- `close_all_print_db()` closes every open TDB, removes entries from the list, zeroes, and frees them.
- `get_printer_notify_pid_list()` fetches `NOTIFY_PID_LIST_KEY`, validates record size, and optionally removes dead or zero-refcount entries.

## Control Flow

Lookup first scans `print_db_head` for a matching open `printer_name`. If found, it promotes the entry and returns it. If the cache has reached `MAX_PRINT_DBS_OPEN`, the least-recently-used entry with zero references is closed, cleared, and reused. Otherwise a new entry is allocated and added to the list. Opening builds `cache_path("printing/") + printername + ".tdb"`, temporarily becomes root when needed, and opens the TDB with `O_RDWR|O_CREAT` mode `0600`.

Notification list fetching reads a single TDB record. If the record size is not a multiple of 8 bytes, it is deleted as corrupt. When cleaning is requested, the helper walks pid/refcount pairs and removes entries where the process no longer exists or the refcount is zero, preserving the current process.

## State and Persistence

Open DB handles and reference counts are process-local in `print_db_head`. Persistent records live in one TDB per printer under the printing cache directory. The notification list record is an array of 8-byte entries: pid followed by refcount.

## Dependencies and Integration Points

This file depends on Samba TDB logging, `cache_path()`, privilege switching, `fstring` helpers, process-existence checks, and the `struct tdb_print_db` definition from printing headers. `printing.c` calls these functions for nearly every print job and queue operation.

## Risks and Edge Cases

- A leaked `release_print_db()` would pin a DB handle and reduce the effectiveness of LRU recycling.
- `get_printer_notify_pid_list()` can leave altered list contents in memory without storing them; callers must store cleaned results when they want persistence.
- The open path uses printer names in filenames, so upstream service-name validation remains important.

## Test Signals

Tests should open more than `MAX_PRINT_DBS_OPEN` printers with mixed refcounts, verify LRU reuse avoids referenced handles, validate close-all cleanup, and exercise corrupt notification records plus stale PID cleanup.
