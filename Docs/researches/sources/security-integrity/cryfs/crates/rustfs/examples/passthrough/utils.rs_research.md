# sources/security-integrity/cryfs/crates/rustfs/examples/passthrough/utils.rs

Purpose: Shared conversion helpers for passthrough metadata and timestamps.

Important APIs/types/functions: `convert_metadata` maps `std::fs::Metadata` to `NodeAttrs`, deriving mode, uid/gid, size, block count, and times. `convert_timespec` maps `SystemTime` to nix `TimeSpec`.

Control flow: metadata conversion inspects Unix metadata extensions and file type bits. Time conversion handles `SystemTime` relative to Unix epoch.

State and persistence behavior: no state; converts host filesystem state into rustfs common structs.

Dependencies and integration points: used by passthrough dir, node, symlink, and openfile code.

Risks: platform assumptions are Unix-heavy. Time before epoch and nanosecond conversion need careful error handling depending on implementation. Mode mapping must preserve node-kind bits expected by rustfs.

Test signals: tests should cover regular file, dir, symlink metadata, block counts, permissions, uid/gid, and pre/post-epoch timestamps.
