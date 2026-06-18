<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/unicode.c -->
# sources/user-network-fs/libsmb2/lib/unicode.c

Purpose: Implements UTF-8 validation plus conversion between UTF-8 and SMB-compatible UTF-16LE strings.

Important APIs, types, and functions: Internal helpers `l1`, `validate_utf8_cp`, `validate_utf8_str`, and `utf16_size`; public functions `smb2_utf8_to_utf16` and `smb2_utf16_to_utf8`.

Control flow: UTF-8 to UTF-16 first validates and counts code units, allocates `struct smb2_utf16`, then replays decoding while writing little-endian code units and surrogate pairs. UTF-16 to UTF-8 computes output size while replacing malformed surrogate sequences, allocates a NUL-terminated string, then encodes each code unit/pair.

State and persistence behavior: Allocates returned strings/structures for callers. It does not retain state. Invalid UTF-8 returns NULL; invalid UTF-16 is converted with replacement characters.

Dependencies and integration points: Depends on portable endian macros and libsmb2 private UTF-16 type. Integrated with path, filename, and DCE/RPC text handling.

Risks: `validate_utf8_cp` advances through continuation bytes without an explicit input-end parameter, relying on NUL termination; truncated multibyte data can read past the logical character. Output length uses `int`, so extremely long names could overflow length arithmetic.

Test signals: Indirect coverage through DCE/RPC UTF-16 coder tests and SMB path operations; no direct fuzz or invalid-sequence unit test in this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/unicode.c -->
