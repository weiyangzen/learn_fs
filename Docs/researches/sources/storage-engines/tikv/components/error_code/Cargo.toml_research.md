<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/error_code/Cargo.toml -->
# sources/storage-engines/tikv/components/error_code/Cargo.toml

Purpose: this manifest defines the `error_code` crate, a non-published TiKV workspace component that centralizes structured error-code constants and a generator binary. The crate is Apache-2.0 licensed, uses Rust 2021, and exposes `src/lib.rs` as library `error_code`.

Important APIs and build targets: the manifest declares one binary target, `error_code_gen`, at `bin.rs`. That binary generates the `etc/error_code.toml` catalog from selected module-level `ALL_ERROR_CODES` vectors. The library target exports the `ErrorCode` type, `ErrorCodeExt` trait, the `define_error_codes!` macro expansion products, and domain modules such as `raftstore`, `storage`, `pd`, and `cloud`.

Dependencies and integration points: `lazy_static` is required by the macro to produce `ALL_ERROR_CODES`; `kvproto` and `raft` are required for conversion implementations over protobuf and raft errors; `tikv_alloc` installs TiKV allocation behavior. The component is consumed by other TiKV crates to attach stable textual error identifiers such as `KV:Storage:Timeout`.

State and persistence behavior: the manifest has no runtime state itself, but it wires the binary that writes a persistent TOML file under `./etc/error_code.toml` when run from the repository root.

Risks: the generator binary currently enumerates only a subset of modules, omitting `backup_stream` and `causal_ts`; manifest readers should not assume every module constant is represented in the generated TOML. The crate also uses nightly-only `min_specialization` in `lib.rs`, so it depends on TiKV's toolchain assumptions.

Test signals: no manifest tests exist here; correctness is covered by library tests in `src/lib.rs` and by compilation of consumers that rely on the exported constants and conversion traits.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/error_code/Cargo.toml -->
