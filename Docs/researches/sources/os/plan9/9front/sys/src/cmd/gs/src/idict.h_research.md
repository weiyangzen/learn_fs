# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/idict.h

Declares the dictionary package interface and exposes first-level dictionary layout.

Key points:
- `dict_s` stores `values`, `keys`, `count`, `maxlength`, and allocator `memory` refs.
- Exposes layout to support fast access checking and lookup.
- Declares `dict_max_size` and `dict_auto_expand`.
- Declares allocation, access-ref helpers, read/write checks, find, string-find, put, string-put, undef, length, capacity, max index, copy, resize, grow, unpack, enumeration, and index lookup functions.
- Documents error behavior for lookup, insertion, copy, resize, and enumeration.
- Defines hash and rounding helpers, with different small/large memory behavior.
- Defines `dict_max_non_huge` threshold and explains huge dictionary fallback.

Research notes:
- This public internal header intentionally leaks representation for speed.
- Hashing assumes name indexes are already sufficiently scattered.
