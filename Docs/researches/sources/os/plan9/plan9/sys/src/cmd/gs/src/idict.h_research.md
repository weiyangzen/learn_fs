# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/idict.h

Dictionary package interface. It exposes first-level dictionary layout for performance:
- `values`
- `keys`
- `count`
- `maxlength`
- `memory`

Declares dictionary allocation, find, put, undef, length/capacity, copy, resize, grow, unpack, and enumeration APIs. It also defines access-check macros and hash/rounding algorithms.

Performance notes:
- On larger-memory systems dictionary sizes round to powers of two where possible.
- Huge dictionaries fall back to slower modulo logic.
- Fast clients use internal hash macros and dictionary layout.
