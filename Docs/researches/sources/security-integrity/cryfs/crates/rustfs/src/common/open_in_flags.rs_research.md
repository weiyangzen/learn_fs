# sources/security-integrity/cryfs/crates/rustfs/src/common/open_in_flags.rs

Purpose: typed wrapper for incoming open flags.

Important APIs: `OpenInFlags { flags: i32 }`, derived `From`/`Into`, and `Debug`.

Control flow and state: no behavior; it preserves the raw FUSE/POSIX flags for filesystem implementations.

Dependencies and integration: used by high-level `open`, `create`, `opendir`, release methods, object `File::into_open`, and directory creation APIs.

Risks and tests: no bit-level helpers or validation, so callers must interpret flags manually. TODOs in adapters note missing wrappers for many raw flag parameters.
