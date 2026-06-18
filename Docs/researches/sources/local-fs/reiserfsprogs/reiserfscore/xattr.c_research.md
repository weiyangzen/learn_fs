# File Research: sources/local-fs/reiserfsprogs/reiserfscore/xattr.c

Extended attribute and ACL helper code for ReiserFS userspace. It implements checksum calculation compatible with kernel-style partial checksums, validates xattr headers, and counts ACL entries.

Major responsibilities:
- `from32to16()` folds a 32-bit checksum into 16 bits.
- `do_csum()` computes an alignment-aware checksum over an arbitrary buffer.
- `csum_partial()` adds a prior partial checksum to a newly computed buffer checksum.
- `reiserfs_xattr_hash()` returns the xattr data hash.
- `reiserfs_check_xattr()` verifies xattr body length, magic, and hash compatibility.
- `reiserfs_acl_count()` derives the number of ACL entries from serialized ACL size.

Important implementation details:
- `do_csum()` handles odd byte alignment and endian-dependent byte placement.
- `reiserfs_check_xattr()` accepts either exact stored hash or folded stored hash, preserving compatibility with older encodings.
- ACL counting supports the first four short entries and then full ACL entries, returning `-1` for malformed sizes.

Dependencies and interactions:
- Includes system ACL definitions and `reiserfs_lib.h` for xattr/ACL structures and endian helpers.
- Intended for tools that inspect or validate ReiserFS xattr bodies and POSIX ACL item payloads.

Risks and notes:
- The checksum implementation uses unaligned casts to `unsigned short *` and `unsigned int *`; this matches legacy low-level style but can be architecture-sensitive.
- `reiserfs_check_xattr()` treats any nonzero magic/hash result as validity, returning boolean-style success rather than a negative errno except for too-short input.
