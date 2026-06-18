# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zstring.c

## Purpose
Implements Ghostscript string allocation, name-to-string conversion, and string search/match operators.

## Key Elements
Defines `.bytestring`, `string`, `.namestring`, `anchorsearch`, `search`, `.stringbreak`, and `.stringmatch`.

## Behavior/Risks
`string` allocates VM-managed strings with `ialloc_string` and enforces `max_string_size`; `.bytestring` allocates byte arrays as structures. `anchorsearch` and `search` return PostScript-style segmented string results with boolean success markers. `.stringbreak` searches for any byte from a delimiter string and explicitly handles embedded NUL bytes. `.stringmatch` supports string/name pattern matching and treats a one-character `*` pattern as matching non-string/name objects.

## Dependencies
Uses Ghostscript allocation, name, VM-space, operand, and store APIs plus `gsutil.h` for `string_match`.
