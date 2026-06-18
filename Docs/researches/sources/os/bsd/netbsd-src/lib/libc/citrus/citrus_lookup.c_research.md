# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_lookup.c

Unified sequential and keyed lookup interface over compiled `.db` files or plain text files.

Key behavior:
- `_citrus_lookup_seq_open` first tries `<name>.db`; if absent, falls back to plain `<name>`.
- DB mode maps the compiled lookup DB, opens it with magic `LOOKUP\0\0`, supports indexed iteration and locator-based repeated keyed lookup.
- Plain mode maps text, ignores comments beginning with `#`, trims whitespace, parses first token as key, and returns the rest as data.
- Supports optional case-insensitive keys by lowercasing stored search keys.
- `_citrus_lookup_simple` opens, performs one lookup, copies data into caller buffer, and closes.

Used heavily for alias files, `iconv.dir`, `mapper.dir`, ESDB directory files, and pivot data.
