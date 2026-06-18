# sources/security-integrity/cryfs/crates/utils/src/path/join.rs

Purpose: allocation-conscious helper to join multiple `Path` components with standard `PathBuf::push` semantics.

Important APIs/types/functions: `path_join(components: &[&Path]) -> PathBuf`.

Control flow: precomputes approximate capacity by summing component OS string lengths plus separators, creates `PathBuf::with_capacity`, then pushes each component in order. Absolute later components reset prior path just like `PathBuf::push`.

State/persistence: returns a new `PathBuf`; no external state.

Dependencies/integration: benchmarked in `benches/path.rs`; public through `path/mod.rs`.

Risks: capacity calculation uses `OsStrExt::len`-like API and is only a performance hint. Semantics intentionally match `PathBuf::join`, including absolute component replacement, which may surprise callers expecting concatenation.

Test signals: exhaustive nested tests compare zero to four components against chained standard joins over empty, root, absolute, relative, and double-slash paths.
