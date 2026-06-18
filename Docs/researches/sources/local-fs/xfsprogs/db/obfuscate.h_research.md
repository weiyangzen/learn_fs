# File Research: sources/local-fs/xfsprogs/db/obfuscate.h

## Purpose
Declares name obfuscation helpers shared by metadump and hash-collision tooling.

## Interfaces
- `is_invalid_char(c)` identifies slash and NUL as invalid generated name bytes.
- `obfuscate_name()` performs hash-preserving obfuscation.
- `find_alternate()` creates deterministic same-hash alternate names.
