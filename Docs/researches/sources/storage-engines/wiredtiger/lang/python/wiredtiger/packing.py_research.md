# sources/storage-engines/wiredtiger/lang/python/wiredtiger/packing.py

## Purpose
This module implements WiredTiger's variable-length format packing and unpacking for Python callers.

## Important APIs, Types, and Functions
The public APIs are `pack(fmt, *values)` and `unpack(fmt, s)`. `__get_type` parses the optional format prefix and accepts only variable-length encoding. `__unpack_iter_fmt` parses repeat counts and format characters. `__pack_iter_fmt` associates parsed items with values. `pack_int` and `unpack_int` handle integral encoding.

## Control Flow
`unpack` handles padding, strings/raw data (`S`, `s`, `U`, `u`), bit fields (`t`), signed/unsigned bytes (`b`, `B`), and variable-length integers. `pack` mirrors that behavior: it emits padding, truncates/pads fixed strings, NUL-terminates unsized `S`, length-prefixes non-final `u` and `U`, validates bit fields, translates signed bytes by adding `0x80`, and packs other integers.

## State and Persistence Behavior
The module is stateless, but emitted bytes are persistent application key/value encodings and must remain compatible with WiredTiger C semantics.

## Dependencies and Integration Points
It depends on `packutil` and `intpacking` and is exported as part of the `wiredtiger` package.

## Risks and Edge Cases
Only variable-length encoding is supported. Empty format returns `()`, which differs from byte-oriented `empty_pack`. String/bytes conversions can surprise binary callers. Malformed input can raise low-level exceptions. Bit fields over 8 bits or out-of-range values are rejected.

## Test Signals
Round-trip tests should cover all documented format characters, repeat counts, empty formats, string padding/truncation, final and non-final raw fields, bit-field validation, signed byte ordering, and rejection of non-variable prefixes.
