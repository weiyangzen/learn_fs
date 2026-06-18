# sources/user-network-fs/samba/source3/printing/print_svid.c

Purpose: discovers printers on SysV/XPG4 or HPUX systems by parsing `lpstat` output into the shared pcap cache.

Important API: under `SYSV` or `HPUX`, `sysv_cache_reload(struct pcap_cache **_pcache)` runs `/usr/bin/lpstat -v`, parses lines like `device for name: ...` or `system for name: ...`, and adds each printer name. Without those platform macros, the file defines only a dummy symbol.

Control flow: command arguments are built as a list and executed with `file_lines_ploadv()`. On HPUX, if `lpstat -v` returns no lines, it checks `lpstat -r`; a running scheduler with no printers is treated as success with an empty list. Each output line skips leading words, handles an extra `for`, ignores `remote to`, truncates at `:`, and adds the result.

State and persistence: creates only a transient `pcap_cache` list. Persistent replacement is handled by `pcap.c`.

Dependencies and integration: selected when `lp_printcapname()` is `lpstat` and build flags match. Depends on external `lpstat`, Samba command-output helpers, talloc string lists, and pcap cache functions.

Risks: output parsing is format-dependent and may mis-handle localized `lpstat` output. The HPUX scheduler path assumes `scheduler` is non-null before dereferencing. Tests should cover normal SysV output, HPUX empty-printer scheduler states, malformed lines, `remote to` filtering, command failure, and zero-printer success semantics.
