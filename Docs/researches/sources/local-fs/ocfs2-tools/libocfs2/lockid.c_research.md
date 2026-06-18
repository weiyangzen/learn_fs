# File Research: sources/local-fs/ocfs2-tools/libocfs2/lockid.c

Encodes, decodes, and prints OCFS2 lock resource names.

Lock type mapping:
- `ocfs2_get_lock_type()` maps single-character lock prefixes to enum types: metadata, data, super, rename, rw, dentry, open, and flock.
- Unknown prefixes return `OCFS2_NUM_LOCK_TYPES`.

Encoding:
- `ocfs2_encode_lockres()` writes standard lock names as type char, pad, 16 hex block number, and 8 hex generation.
- Dentry locks are special: they include printable parent inode text followed by the target inode encoded in binary big-endian form, matching filesystem lock naming.

Decoding:
- `ocfs2_decode_lockres()` parses standard locks with `sscanf()`.
- For dentry locks, it parses the parent from text and tries to parse the inode payload from the binary-position substring using `strtoull(..., 16)`. This is asymmetric with the binary `memcpy()` encoding and appears fragile for arbitrary binary bytes.

Printing:
- `ocfs2_printable_lockres()` converts dentry binary inode payload back to a printable suffix using `bswap_64()` and truncates to 32-bit in formatting; non-dentry locks are copied as strings.

Context:
- Supports tools/debug output for lock names used by the cluster DLM and filesystem lock debugging documented in `ocfs2.7.in`.
