# sources/user-network-fs/samba/source3/printing/print_aix.c

Purpose: AIX-specific printcap loader that parses qconfig-style files and returns discovered virtual printers through the shared `pcap_cache` interface.

Important API: under `AIX`, `aix_cache_reload(struct pcap_cache **_pcache)` opens `lp_printcapname()`, scans stanzas, skips comments and the `bsh` entry, and adds printer names when a stanza appears to represent a virtual printer. Without `AIX`, the file only defines a dummy symbol.

Control flow: the parser tracks a small state machine. State 0 looks for a top-level `name:` stanza. State 1 scans indented stanza lines; a `backend` line indicates a device, while a `device` line or a new top-level line causes the saved name to be added.

State and persistence: creates a transient `pcap_cache` list. Durable replacement is performed later by `pcap_cache_replace()` in `pcap.c`.

Dependencies and integration: depends on `fgets_slash()`, AIX qconfig formatting, loadparm printcap name, talloc, and shared pcap cache helpers. It is selected by `pcap_cache_reload()` when the configured printcap name contains `/qconfig`.

Risks: parser heuristics are qconfig-specific and may misclassify unusual stanzas. Some paths use `SAFE_FREE(line)` for talloc memory, which is notable beside `TALLOC_FREE(line)` in nearby code. Tests should cover comments, `bsh` skip, backend-only devices, virtual devices, stanza transitions, and open/read failures.
