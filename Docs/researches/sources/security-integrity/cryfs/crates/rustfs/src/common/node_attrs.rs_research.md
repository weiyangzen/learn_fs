# sources/security-integrity/cryfs/crates/rustfs/src/common/node_attrs.rs

Purpose: shared file metadata struct.

Important APIs: `NodeAttrs` fields include `mode`, `uid`, `gid`, `num_bytes`, optional `num_blocks`, `atime`, `mtime`, `ctime`, and `nlink`. A helper formats timestamps for custom `Debug`.

Control flow and state: plain copyable metadata. The debug derive hides raw `SystemTime` formatting behind human-readable `OffsetDateTime`.

Dependencies and integration: returned by object nodes, high-level `AttrResponse`, low-level `ReplyEntry`/`ReplyAttr`/`ReplyCreate`, and tests.

Risks and tests: no validation ensures mode and node kind agree. Optional block count lets backends omit block accounting. Test helpers construct deterministic-like metadata around `SystemTime::now`.
