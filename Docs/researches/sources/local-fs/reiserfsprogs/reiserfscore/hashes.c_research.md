# File Research: sources/local-fs/reiserfsprogs/reiserfscore/hashes.c

## Purpose
`hashes.c` implements the directory-name hash functions used by ReiserFS directory ordering and validation.

## Main Responsibilities
- Provides the TEA-based keyed hash.
- Provides the legacy Rupasov/Yura hash.
- Provides the legacy `r5` hash.
- Contains a disabled standalone test harness under `#if 0`.

## Key Functions
- `keyed_hash()` hashes a signed character buffer using a TEA-derived Davis-Meyer construction. It processes 16-byte chunks with partial rounds, pads the tail with repeated length bytes, then performs full rounds.
- `yura_hash()` converts name bytes into a decimal-like accumulator with padding-style loops, then shifts the result left by 7.
- `r5_hash()` accumulates each byte’s high/low nibbles and multiplies by 11.

## Data and Control Flow
The hash functions return `u32` values. Higher-level code masks or extracts hash/generation portions when comparing directory entry offsets. `node_formats.c` registers these functions in the hash table and uses them to detect or verify the active filesystem hash.

## Integration Points
- Used through `hashf_t` mappings in `node_formats.c`.
- Directory validation calls `hash_value()`/`GET_HASH_VALUE()` against these functions.
- Superblock hash-code conversion maps stored hash IDs to these function pointers.

## Risks and Edge Cases
- `keyed_hash()` builds 32-bit words from `signed char`; negative `msg[i]` values can sign-extend before conversion on platforms where char values exceed ASCII.
- It uses deliberate null writes in impossible guard branches, a legacy crash-on-bug pattern.
- `yura_hash()` has unusual loops that depend on integer overflow behavior for long names.
- These are compatibility hashes, not cryptographic security primitives.

## Testing Signals
Useful tests should verify known ReiserFS hash vectors for `tea`, `rupasov`, and `r5`, including empty names, short names, long names, non-ASCII byte values, and names whose hash maps to directory offset masks.
