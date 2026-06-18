# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/utf8n.h

## Purpose
Declares the userspace UTF-8 normalization interface copied from Linux kernel logic so e2fsprogs hashes and validates casefolded names consistently with ext4.

## API Surface
- Unicode version helpers: `UNICODE_AGE`, `utf8version_is_supported()`, `utf8version_latest()`.
- Normalization data lookup: `utf8nfdi()` and `utf8nfdicf()`.
- Age checks: `utf8agemax/min()` and length-bounded variants.
- Normalized length checks: `utf8len()` and `utf8nlen()`.
- Streaming normalization cursor: `struct utf8cursor`, `utf8cursor()`, `utf8ncursor()`, and `utf8byte()`.

## Integration
Used by ext4 encoding/casefold support where userspace tools must match kernel normalization and hashing semantics.

## Risks / Notes
The header is only declarations and shared data-contract definitions; correctness depends on the generated/table implementation matching kernel behavior.
