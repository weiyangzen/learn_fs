## sources/security-integrity/encfs/build.rs

Purpose: Build script that compiles `proto/encfs_config.proto` into Rust code for the V7 config format using a vendored `protoc`.

Important APIs and functions: `main`, `protoc_bin_vendored::protoc_bin_path`, unsafe `std::env::set_var("PROTOC", ...)`, `prost_build::Config::new().compile_protos`. Control flow obtains the vendored compiler path, exposes it through `PROTOC`, compiles the proto from `proto` include root, and returns `Ok(())` or panics on compile failure.

State and persistence: Generates Rust protobuf bindings in Cargo `OUT_DIR`; no source-tree output. Dependencies are build dependencies in `Cargo.toml`. Integration is consumed by `src/config_proto.rs` using `include!(concat!(env!("OUT_DIR"), "/encfs.v7.rs"))`. Risk: build fails if vendored protoc cannot be located or proto compilation errors; the unsafe env mutation is acceptable in single-threaded build-script context.
