# sources/security-integrity/ecryptfs-utils/src/libecryptfs/ecryptfs-stat.c

## Purpose
Parses the fixed front matter of an eCryptfs file header into a user-space crypt-stat structure. It extracts original file size, validates the eCryptfs marker, maps on-disk flags to local flags, records file version, and parses header extent metadata.

## Important APIs, types, and functions
- `ecryptfs_parse_stat` is the public parser.
- `swab64`, `host_is_big_endian`, and network-byte-order conversions normalize disk data.
- `ecryptfs_contains_ecryptfs_marker`, `ecryptfs_process_flags`, and `ecryptfs_parse_header_metadata` parse the header fields.
- `ecryptfs_flag_map` maps known on-disk bits to local crypt-stat flags.

## Control flow
`ecryptfs_parse_stat` first checks that enough bytes are available for the size, marker, and flags. It zeroes the output structure, reads and byte-swaps the file size as needed, validates the marker, processes flags, then parses header extent metadata with validation enabled. Packet-set parsing is explicitly left commented out.

## State and persistence behavior
The function only fills the caller-provided `struct ecryptfs_crypt_stat_user`; it does not allocate or persist state. It reads from a caller-supplied header buffer and prints diagnostics on malformed input.

## Dependencies and integration points
Depends on constants and output structure definitions in `ecryptfs.h`. It is a library-side companion for utilities that inspect encrypted file headers without mounting them.

## Risks and edge cases
The parser trusts the caller's buffer after the initial minimum check and does not verify all subsequent field availability against `buf_size`. Endianness handling is manual and should be treated carefully on uncommon architectures. Unknown on-disk flags are ignored rather than rejected. Diagnostics go to stdout via `printf`, not syslog or an error object.

## Test signals
Tests should feed known-good headers for little- and big-endian interpretations, bad marker pairs, too-short buffers, invalid header extents below `ECRYPTFS_MINIMUM_HEADER_EXTENT_SIZE`, and combinations of HMAC/encrypted/xattr flags.
