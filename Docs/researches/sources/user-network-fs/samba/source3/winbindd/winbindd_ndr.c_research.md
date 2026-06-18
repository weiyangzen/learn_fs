# sources/user-network-fs/samba/source3/winbindd/winbindd_ndr.c

## sources/user-network-fs/samba/source3/winbindd/winbindd_ndr.c

`winbindd_ndr.c` provides debug/NDR printers for core winbindd runtime structures. It does not implement protocol behavior; it makes `winbindd_child`, `winbindd_cm_conn`, `winbindd_methods`, and `winbindd_domain` inspectable through Samba's NDR print framework.

`ndr_print_winbindd_child()` prints process id, domain pointer, logfile, and lockout policy event pointer. `ndr_print_winbindd_cm_conn()` prints RPC client pointers and policy handles for SAMR, LSA, and Netlogon connections. `ndr_print_winbindd_methods()` compares a method-table pointer against known global method tables (`msrpc_methods`, optionally ADS methods, passdb methods, reconnect wrappers) and prints a symbolic backend name or `UNKNOWN`. `ndr_print_winbindd_domain()` prints domain identity, trust flags/type/attributes, booleans such as `initialized`, `active_directory`, `primary`, `internal`, and `online`, timing and sequence state, backend identity, connection state, child array entries, and online-check event pointers.

The file has no persistent state and no ownership changes. It depends on generated NDR printers for Netlogon, security, and LSA structures, the `libndr` print API, and external method-table symbols. Integration points are debug dumps, messaging handlers that print domain lists, diagnostics, and developer troubleshooting.

Risks are diagnostic rather than behavioral: stale method-table comparisons can report `UNKNOWN` for new backends; pointer printing avoids recursive domain printing for child domains; and sensitive topology/connection information may appear at high debug levels. Test signals include compiling with and without `HAVE_ADS`, dumping domains with multiple children, reconnect method identification, and ensuring debug dumps do not dereference NULL domains.
