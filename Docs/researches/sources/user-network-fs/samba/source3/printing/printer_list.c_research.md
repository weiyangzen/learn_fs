# sources/user-network-fs/samba/source3/printing/printer_list.c

Purpose: persistent database of currently known system printers. It stores printer name, comment, location, and refresh timestamp in `printer_list.tdb` under the lock path.

Important APIs and functions: `printer_list_get_printer()` fetches one printer by case-insensitive key and returns comment/location/refresh time. `printer_list_printername_exists()` checks for a printer key. `printer_list_set_printer()` packs and stores printer data with uppercase key semantics. `printer_list_mark_reload()` stores the global last-refresh timestamp. `printer_list_get_last_refresh()` reads that timestamp. `printer_list_clean_old()` traverses writable records and deletes printer entries older than the last refresh. `printer_list_read_run_fn()` traverses read-only records and invokes a callback for each printer.

Control flow: `get_printer_list_db()` lazily opens `printer_list.tdb` with `db_open()` and caches the `db_context`. Data is packed as high/low 32-bit monotonic time plus three strings. Cleanup compares each entry timestamp with the global timestamp written at reload start.

State and persistence: global static `printerlist_db` is the process cache for the DB handle. Durable records use `PRINTERLIST/PRN/<name>` and `PRINTERLIST/GLOBAL/LAST_REFRESH`.

Dependencies and integration: used by `pcap_cache_replace()` to publish discovery results and by printer enumeration/name checks elsewhere. Depends on dbwrap/TDB, lock paths, monotonic time, and Samba NTSTATUS conventions.

Risks: if reload marks the timestamp and then fails before storing printers, cleanup is only called on successful reload, preserving old entries. Case-insensitive key storage/fetch is important for share-name behavior. Traversal callbacks treat unpack failures as DB corruption. Tests should cover first open failure, case-insensitive lookup, empty comment/location normalization, stale cleanup, timestamp packing on 32/64-bit time, read traversal skipping the global key, and corruption handling.
