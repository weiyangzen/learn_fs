## sources/security-integrity/encfs/src/config_proto.rs

Purpose: Thin generated-code bridge for EncFS V7 protobuf bindings. It includes the Rust module generated from `proto/encfs_config.proto` by `build.rs`.

Important APIs and functions: `include!(concat!(env!("OUT_DIR"), "/encfs.v7.rs"))`. Control flow is compile-time inclusion: Cargo runs the build script, prost writes generated code to `OUT_DIR`, and this module exposes generated messages/enums under `crate::config_proto`.

State and persistence: No runtime state; depends on generated build output. Dependencies are `build.rs`, `prost-build`, vendored protoc, and the proto schema. Integration is used heavily by `config.rs` for V7 load/save/hash conversion. Risk: IDEs or tools that do not run build scripts may not resolve generated symbols; build failures in proto generation break this module.
