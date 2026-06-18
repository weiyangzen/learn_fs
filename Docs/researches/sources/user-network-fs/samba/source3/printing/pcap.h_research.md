# sources/user-network-fs/samba/source3/printing/pcap.h

Purpose: shared interface for printcap cache management and platform-specific printer discovery backends.

Important APIs and types: forward declares `struct pcap_cache` and exposes cache list operations, `pcap_cache_reload()`, `pcap_printername_ok()`, and backend reload functions for AIX, CUPS, iPrint, SysV/HPUX, and standard printcap files.

Control flow and integration: `pcap.c` uses the backend declarations to select discovery at runtime and build a cache list, while backend files call `pcap_cache_add_specific()` to populate that list. Other printing code can iterate a specific cache with `pcap_printer_fn_specific()`.

State and persistence: the header abstracts `pcap_cache` internals so backends can append/destroy but not inspect representation. Persistent storage is handled indirectly through `pcap_cache_replace()` and `printer_list`.

Dependencies: uses `tevent_context`, `messaging_context`, and `bool` from Samba includes; conditional backend availability is controlled at compile time in implementation files.

Risks and test signals: `pcap_printername_ok()` is declared here but not implemented in `pcap.c`, so consumers depend on another translation unit. Build coverage across feature flag combinations (`HAVE_CUPS`, `HAVE_IPRINT`, `AIX`, `SYSV`, `HPUX`) is important.
