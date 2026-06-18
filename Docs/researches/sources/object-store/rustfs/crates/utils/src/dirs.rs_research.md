# sources/object-store/rustfs/crates/utils/src/dirs.rs

Purpose: Best-effort project root discovery helper.

Important APIs: `get_project_root() -> Result<PathBuf, String>`.

Control flow: Tries `CARGO_MANIFEST_DIR`, then derives from `current_exe` by popping executable and target profile directories, then derives from current directory by popping one level. Returns a string error only if all methods fail.

State and dependencies: Stateless, using `std::env`, `PathBuf`, and tracing debug logs.

Integration points: General utility likely used by tests/tools needing a root path.

Risks and tests: The `current_exe` and `current_dir` heuristics are build-layout assumptions and can return the wrong root outside Cargo target layouts. Unit test only asserts returned path exists, not that it is the workspace or crate root.
