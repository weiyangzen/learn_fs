# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/parsefields.c

Comma-separated output-field parser.

Key behavior:
- Parses requested field names against a `wordtab_t` table.
- Allows `field=header` overrides; empty header sets global `nohdrfields`.
- Produces a sentinel-terminated allocated `wordtab_t` list.

Research notes:
- Unknown fields call `exit(1)`.
- Uses `reallocarray()` and aborts on allocation failure after initial allocation.
