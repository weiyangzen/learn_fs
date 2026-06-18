# File Research: sources/local-fs/ocfs2-tools/extras/decode_lockres.c

Read coverage: complete file read, 149 lines.

Purpose: decodes OCFS2 DLM lock resource names into human-readable lock type, block number, and generation.

Behavior:
- Accepts one or more lockres strings.
- Validates exact OCFS2 lock id length and lock type character.
- Supports metadata, data, superblock, rename, and read/write lock types.
- Parses the 16-hex-digit block number and 8-hex-digit generation from the fixed-format lock name.

Dependencies: local copy of OCFS2 kernel lock-name constants and type characters.

Risk notes:
- The lock format is pasted into the utility; if kernel lock-name encoding changes, this tool can drift.
- It validates length/type but not that pad bytes are exactly `000000`.
