# File Research: sources/local-fs/ocfs2-tools/extras/encode_lockres.c

Read coverage: complete file read, 96 lines.

Purpose: encodes an OCFS2 DLM lock resource name from lock type, block number, and generation.

Behavior:
- Usage: `encode_lockres [M|D|S] [blkno] [generation]`.
- Validates the requested type against metadata, data, and superblock types.
- Formats the lock resource as type + six zero pad bytes + 16 hex digits of block number + 8 hex digits of generation.

Dependencies: local copy of an older/smaller OCFS2 kernel lock-name enum.

Risk notes:
- Encoder supports only `M`, `D`, and `S`, while `decode_lockres.c` also knows rename and read/write locks.
- Uses `atoll()` for numeric input, so malformed strings can silently become zero.
