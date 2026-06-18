# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_esdb.c

Encoding Scheme Database loader.

Key behavior:
- `_citrus_esdb_alias` resolves encoding aliases through `_PATH_ESDB/esdb.alias`.
- `_citrus_esdb_open` resolves aliases, finds an ESDB filename through `esdb.dir`, maps it, and converts the DB into `_citrus_esdb`.
- `conv_esdb` validates magic/version, reads encoding name, optional variable string, charset count, optional invalid character, and per-charset csid/name pairs.
- `_citrus_esdb_close` frees allocated strings and charset arrays.
- `_citrus_esdb_get_list` merges alias and directory entries, lowercases names, removes duplicates, and returns a dynamically allocated list.

Dependencies:
- Uses Citrus lookup for alias/dir text or compiled lookup DBs and Citrus DB for actual ESDB content.
