# sources/security-integrity/cryfs/crates/rustfs/src/common/atime_update_behavior.rs

Purpose: models mount-style access-time policies for files, symlinks, and directories. It is serializable and can be used by filesystems to decide whether a read should update atime.

Important APIs: `AtimeUpdateBehavior` variants are `Noatime`, `Strictatime`, `Relatime`, `NodiratimeRelatime`, and `NodiratimeStrictatime`. The public decision methods are `should_update_atime_on_file_or_symlink_read` and `should_update_atime_on_directory_read`.

Control flow and state: the type is stateless. Both decision functions match on the enum and optionally call private `relatime`, which updates when old atime is older than mtime or older than 24 hours relative to the candidate new atime.

Dependencies and integration: uses `serde` for config persistence and `SystemTime`/`Duration`. It is exported through `common/mod.rs` and `lib.rs`.

Risks and tests: there is a TODO for tests. The comment mentions ctime, but the implementation only receives and compares mtime, so ctime-driven relatime behavior is absent. Subtracting 24 hours from `new_atime` assumes the timestamp is representable.
