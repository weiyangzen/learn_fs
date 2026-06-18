# sources/user-network-fs/samba/source3/printing/print_standard.c

Purpose: parses traditional BSD-style printcap files into the shared `pcap_cache` format.

Important API: `std_pcap_cache_reload(const char *pcap_name, struct pcap_cache **_pcache)` opens the configured file, reads continuation-aware lines with `fgets_slash()`, ignores comments and empty records, splits at the first colon, and selects a printer name/comment from `|`-separated aliases.

Control flow: for each record, the first alias without punctuation becomes the printer name. Aliases containing punctuation are treated as human-readable comments. Each discovered name is added to a transient pcap cache. A warning is emitted once if any name exceeds `MAXPRINTERLEN`.

State and persistence: produces only a transient list. `pcap.c` later persists successful reloads to `printer_list.tdb`.

Dependencies and integration: used as the default fallback by `pcap_cache_reload()` when the printcap name is not one of the special backend selectors. Depends on Samba file utilities and pcap cache helpers.

Risks: parsing is intentionally heuristic and local-file-only; it ignores NIS and more complex printcap semantics. Repeated `TALLOC_FREE(pcap_line)` inside alias parsing is unusual but guarded by talloc behavior. Tests should cover continuations, comments, multiple aliases, comments with punctuation, overlong names, missing colon, unreadable files, and allocation failure cleanup.
