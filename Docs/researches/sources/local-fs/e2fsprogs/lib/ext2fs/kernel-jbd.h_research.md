# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/kernel-jbd.h

Defines JBD2 on-disk journal metadata used by e2fsprogs: journal headers, commit headers, block tags, revoke headers, journal superblocks, checksum fields, feature bits, and transaction id helpers.

Key constants include `JBD2_MAGIC_NUMBER`, block type IDs, checksum feature bits, 64-bit and fast-commit incompat features, minimum/default journal sizing, and tag flags such as `JBD2_FLAG_ESCAPE`, `SAME_UUID`, and `LAST_TAG`.

Inline helpers generate feature predicates and setters/clearers for checksum, revoke, 64-bit, async commit, checksum v2/v3, and fast commit. `journal_tag_bytes()` adjusts descriptor tag size based on checksum and 64-bit features.

This is a structural compatibility header, not journal execution logic. Its main risk surface is format drift: these definitions must stay aligned with kernel JBD2 layout because journal replay and mkjournal depend on byte-exact on-disk structures.
