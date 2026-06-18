# sources/user-network-fs/samba/source3/printing/printer_list.h

Purpose: public interface for the persistent printer-list database used by pcap reload and printer enumeration code.

Important APIs: declares lookup (`printer_list_get_printer()`), existence (`printer_list_printername_exists()`), store (`printer_list_set_printer()`), refresh timestamp (`printer_list_get_last_refresh()`, `printer_list_mark_reload()`), cleanup (`printer_list_clean_old()`), and traversal (`printer_list_read_run_fn()`) functions.

Control flow and integration: discovery code marks reload, stores all current printers, then cleans old entries. Enumeration code can fetch one printer or run a callback over all entries. The callback receives name, comment, location, and caller-private data.

State and persistence: the implementation persists records in `printer_list.tdb`; this header defines the API boundary without exposing record formats or dbwrap details.

Dependencies: requires `NTSTATUS`, `TALLOC_CTX`, `time_t`, and `bool` from Samba/core headers.

Risks and test signals: typo-only comments aside, the important contract is ownership: returned comment/location strings are allocated on `mem_ctx`, while traversal callback strings are temporary for the callback duration. Tests should verify callers do not retain traversal pointers beyond callback scope and handle non-OK NTSTATUS values.
