# sources/security-integrity/cryfs/crates/check/Cargo.toml

Purpose: This manifest defines the `cryfs-check` crate and binary. It is a workspace Rust package for checking CryFS vault integrity and reporting structural corruption.

Important APIs and flow: The `[[bin]]` entry names the executable `cryfs-check`. Runtime dependencies include CryFS block/blob/fsblob/config/CLI/version crates, async/runtime libraries, `clap`, `futures`, `tokio`, `thiserror`, `console`, `itertools`, and logging support.

State and persistence: The crate depends on blockstore, fsblobstore, config, and local-state-aware CLI utilities, but the application wraps the blockstore read-only during checking. Dev dependencies enable fixture-based integration tests that create and corrupt temporary filesystems.

Dependencies and integration: The `check_for_updates` feature forwards to `cryfs-cli-utils/check_for_updates`. Dev dependencies enable `testutils` features on fsblobstore, blockstore, and config crates, plus `rstest`, `pretty_assertions`, `rand`, and `tempfile`.

Risks and test signals: The manifest has broad internal crate coupling, which is expected for an end-to-end checker. Feature forwarding means CLI behavior may change with workspace feature selection, and integration tests rely on the testutils features being available.
