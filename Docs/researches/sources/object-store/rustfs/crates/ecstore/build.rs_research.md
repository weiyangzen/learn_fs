# sources/object-store/rustfs/crates/ecstore/build.rs

Purpose: build script that runs `shadow_rs::ShadowBuilder` for the ecstore crate.

Important API: `main` returns `shadow_rs::SdResult<()>`, invokes `ShadowBuilder::builder().build()?`, then returns `Ok(())`.

Control flow: Cargo executes this before compiling the crate. `shadow-rs` emits generated build metadata such as package version, commit hash, tag, and commit date into the build output.

State and persistence: writes generated build metadata into Cargo's build output directory. It does not write repository files directly.

Dependencies and integration points: paired with the build dependency in `Cargo.toml`. Runtime code in `admin_server_info.rs` imports `shadow!(build)` and formats version/commit data through `get_commit_id`.

Risks: builds may fail or lose metadata if the source tree lacks expected VCS information, depending on `shadow-rs` behavior. Reproducibility depends on how commit/date metadata is captured.

Test signals: no direct tests here; indirect signal is any code depending on `get_commit_id` and build metadata compilation.
