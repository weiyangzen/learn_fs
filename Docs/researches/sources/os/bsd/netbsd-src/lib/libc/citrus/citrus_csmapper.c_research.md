# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_csmapper.c

High-level character-set mapper resolver. It opens direct charset mappers or builds pivoted mapper chains.

Key behavior:
- Maintains a global `_citrus_mapper_area` for `_PATH_CSMAPPER`.
- Resolves source and destination charset aliases through `charset.alias`.
- Returns a persistent `mapper_none` instance when source and destination resolve to the same charset.
- Attempts direct mapper lookup by `src/dst`.
- If direct lookup fails and pivoting is allowed, finds the lowest-cost pivot using compiled `charset.pivot.pvdb` or text `charset.pivot`.
- Opens pivot chains via `mapper_serial` with `src/pivot,pivot/dst`.

Dependencies:
- Uses Citrus lookup, DB, mapper, mmap, BCS, endian helpers, and process-wide rwlock protection for the singleton none mapper.
