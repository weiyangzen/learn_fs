# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zstring.c

## Purpose
Implements Ghostscript string-specific operators that are not handled by generic composite operators.

## Public Surface
- `zstring`: allocates a zeroed PostScript string.
- Private operators: `.bytestring`, `.namestring`, `anchorsearch`, `search`, `.stringbreak`, `.stringmatch`.
- Registered through `zstring_op_defs`.

## Implementation Notes
- `.bytestring` allocates raw bytes and returns an array-structure ref.
- `string` allocates with `ialloc_string`, enforces `max_string_size`, and zero-fills.
- `.namestring` exposes the bytes backing a name.
- `anchorsearch` checks prefix match and returns post/match/boolean according to PostScript convention.
- `search` scans for a pattern and returns post/match/pre/boolean.
- `.stringbreak` searches for any byte from a character-set string without C string APIs, so embedded NULs work.
- `.stringmatch` compares strings or names against wildcard-style patterns via `string_match`.

## Dependencies
Uses Ghostscript allocation, names, VM-space attributes, ref attributes, and utility string matching.

## Risks and Notes
- Several operators adjust `value.bytes` and sizes in-place to create substring views.
- `.stringmatch` treats non-string/name objects as matching only a single `*` pattern.
- Filesystem relevance: none directly; this is interpreter string handling.
