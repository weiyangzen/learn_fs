# sources/security-integrity/cryfs/crates/rustfs/src/common/open_out_flags.rs

Purpose: placeholder for outgoing open flags returned to FUSE.

Important APIs: empty `OpenOutFlags` struct with clone/copy/equality/hash/debug.

Control flow and state: carries no fields today. Adapters return `OpenOutFlags {}` for open/create/opendir.

Dependencies and integration: part of high-level and low-level reply structs.

Risks and tests: missing fields means direct I/O, keep-cache, nonseekable, and similar FUSE open response controls are not modeled yet.
