# sources/storage-engines/wiredtiger/lang/python/wiredtiger/fpacking.py

This module implements fixed-size WiredTiger packing/unpacking using Python `struct`. `pack(fmt, *values)` and `unpack(fmt, s)` are the public APIs; `__wt2struct` maps format prefixes, defaults to big-endian/no-alignment, and maps WiredTiger `r` to `Q`.

`unpack` accumulates struct fields until it reaches `S` or `u`, then handles NUL-terminated strings and raw byte arrays specially. `pack` constructs a struct format, translates `S` to fixed string bytes with a NUL terminator, and adds a length before non-final `u` values. The module is stateless and integrates with `packing.empty_pack`. Risks are Python string/bytes edge cases, embedded NUL truncation, and malformed buffers. Round-trip tests should cover scalars, endian prefixes, `r`, fixed and NUL-terminated strings, final/non-final `u`, and empty formats.
