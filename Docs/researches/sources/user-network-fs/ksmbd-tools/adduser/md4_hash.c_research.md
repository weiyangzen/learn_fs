<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/adduser/md4_hash.c -->
# sources/user-network-fs/ksmbd-tools/adduser/md4_hash.c

## Purpose

Standalone MD4 implementation used to produce SMB NT password hashes after UTF-16LE password conversion.

## Important APIs, Types, and Functions

Exports `md4_init`, `md4_update`, and `md4_final` declared in md4_hash.h. Internal helpers implement the three MD4 rounds, little-endian block conversion, padding, and final digest extraction.

## Control Flow

`md4_update` accumulates bytes into 64-byte blocks, transforms full blocks, and keeps a byte counter. `md4_final` appends MD4 padding and bit length, performs the final transform, writes the little-endian 16-byte digest, and zeroes the context.

## State and Persistence Behavior

State is only `struct md4_ctx`: four hash words, a 16-word block, and byte count. No heap or file state is used.

## Dependencies and Integration Points

Depends on memory functions, asm byteorder helpers, and md4_hash.h.

## Risks and Edge Cases

MD4 is cryptographically broken but required for NT hash compatibility. The code assumes platform integer sizes matching the typedef macros. It is sensitive to endian helper availability.

## Test Signals

Test with RFC1320 MD4 vectors and known NTLM hash vectors after UTF-16LE conversion.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/adduser/md4_hash.c -->
