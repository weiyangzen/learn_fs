# sources/security-integrity/cryfs/crates/utils/src/path/mod.rs

Purpose: public facade for path utilities.

Important APIs/types/functions: declares `component`, `path`, `error`, `iter`, and `join`; re-exports `PathComponent`, `PathComponentBuf`, `AbsolutePath`, `AbsolutePathBuf`, `ParsePathError`, and `path_join`.

Control flow/state: no runtime logic; defines public module surface.

Dependencies/integration: lets callers import validated path types and join helper from `cryfs_utils::path`.

Risks: the unlisted `path.rs` module is an important dependency even though not part of this work item. Public re-exports are semver-sensitive.

Test signals: child modules provide validation and join tests.
