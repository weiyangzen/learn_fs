# sources/user-network-fs/samba/source3/printing/pcap.c

Purpose: central printcap cache coordinator. It builds transient printer lists from backend-specific discovery code and persists the resulting printer inventory into `printer_list.tdb`.

Important APIs and functions: `pcap_cache_add_specific()` appends a printer entry with optional comment/location to a linked list. `pcap_cache_destroy_specific()` frees that list. `pcap_cache_replace()` marks a new reload timestamp, stores each printer into `printer_list`, and removes stale entries. `pcap_cache_reload()` selects the discovery backend based on `lp_printcapname()` and build flags: CUPS, iPrint, SysV/HPUX `lpstat`, AIX qconfig, or standard printcap parsing. `pcap_printer_fn_specific()` iterates a supplied transient list.

Control flow: reload is skipped if `load printers` is disabled or no printcap name is configured. CUPS is special: it performs asynchronous discovery and invokes the post-fill callback itself. Synchronous backends return a `pcap_cache` list; on success, this file replaces the persistent printer list and optionally calls the post-fill callback.

State and persistence: transient cache entries are heap linked-list nodes. Durable state is delegated to `printer_list_mark_reload()`, `printer_list_set_printer()`, and `printer_list_clean_old()`.

Dependencies and integration: integrates with all backend loaders declared in `pcap.h`, loadparm, tevent/messaging for CUPS, and the printer list database. It is the bridge between system printer discovery and Samba share/printer enumeration.

Risks: failed reloads intentionally preserve old persistent entries, which is desirable but can hide stale printers. CUPS asynchronous handling means callers must not assume a successful return means the list is already replaced. `pcap_cache_add_specific()` does not clean up partially allocated fields if later field allocations fail. Tests should cover backend selection, disabled loading, failed reload preserving old entries, successful cleanup of stale entries, and CUPS callback ordering.
