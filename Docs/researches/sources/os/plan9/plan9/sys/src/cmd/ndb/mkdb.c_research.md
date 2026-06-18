# File Research: sources/os/plan9/plan9/sys/src/cmd/ndb/mkdb.c

Converter from merged UUCP/Internet-style host data on stdin into Plan 9 NDB entries on stdout. It classifies tokens as comments, system names, Datakit names, IP addresses, or domain names, groups related tuples, and prints normalized NDB records.

Classification helpers identify Datakit names by alnum plus slash, domains by dot plus alphabetic/hyphen chars, and IPs by dotted digits. `tprint()` emits a preferred `sys = name` first, then indented `dom=`, `ip=`, `dk=`, and additional `sys=` attributes. Some Datakit console paths add `flavor=console`.

The main loop merges adjacent lines that share a domain already in the current tuple set; otherwise it flushes the current NDB entry and starts a new one. Duplicate tuple/type pairs are skipped.

Risks include fixed `tup[64][64]` storage with unchecked `strcpy`, legacy domain/IP parsing, and assumptions about old Datakit naming conventions.
