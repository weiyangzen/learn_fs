<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-cli/src/args/fuse_option/atime_option.rs -->
# sources/security-integrity/cryfs/crates/cryfs-cli/src/args/fuse_option/atime_option.rs

Purpose: parses and normalizes FUSE atime-related mount options into runner-level `AtimeUpdateBehavior`.

Important APIs/types/functions: `AtimeOption` is a clap `ValueEnum` with `atime`, `strictatime`, `noatime`, `relatime`, and `nodiratime`. `to_atime_behavior` folds a slice of options into flags and validates allowed/forbidden combinations.

Control flow: duplicates are accepted. `noatime` dominates `nodiratime`, while `atime` and `relatime` are treated as equivalent and can combine. Conflicts such as `noatime` with `atime`/`relatime`/`strictatime`, or `strictatime` with relatime-style flags, return `anyhow::bail!` errors.

State and persistence: no persistence. Result affects runtime atime update policy passed to `cryfs_runner::Mounter`.

Dependencies/integration: maps directly to `cryfs_runner::AtimeUpdateBehavior` and is selected out of mixed `FuseOption` values by `FuseOption::partition`.

Risks/test signals: local `rstest` coverage exhaustively checks one-flag, duplicate, allowed, and forbidden combinations. Semantics intentionally default to `Noatime` to reduce synchronization conflicts.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-cli/src/args/fuse_option/atime_option.rs -->
