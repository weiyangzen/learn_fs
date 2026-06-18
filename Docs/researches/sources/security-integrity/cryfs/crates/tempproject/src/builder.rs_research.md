# sources/security-integrity/cryfs/crates/tempproject/src/builder.rs

Purpose: builder-pattern API for constructing a temporary binary Cargo project on disk.

Important APIs/types/functions: `TempProjectBuilder { folder, cargo, main }`; `new()` creates a prefixed `TempDir`; `cargo()` and `main()` store file contents; `build()` writes `Cargo.toml` and `src/main.rs` and returns `TempProject`.

Control flow: builder methods consume and return `Self`. `build()` calls `_build_cargo_toml()` then `_build_main_rs()`. Missing required content panics with explicit messages.

State/persistence: owns a `TempDir`; build writes files into that temp folder. Cleanup is delegated to `TempDir` after the resulting `TempProject` drops.

Dependencies/integration: uses `anyhow::Result`, `tempfile::TempDir`, and `TempProject::new`. It is the public creation path re-exported by `lib.rs`.

Risks: missing `cargo()` or `main()` is a panic, not a recoverable error. `create_dir` for `src` fails if the directory already exists; no support for extra files or library projects.

Test signals: `tests/simple.rs` covers success and panic cases for missing builder fields.
