# sources/object-store/rustfs/crates/ecstore/tests/protobuf_bytes_regression_test.rs

Purpose: compile-time regression test that protobuf binary payload fields remain `bytes::Bytes` rather than `Vec<u8>` or another buffer type.

Important APIs and flow: `expect_bytes(_: &Bytes)` is a type assertion helper. The single test constructs default node-service messages and passes `file_info_bin`, `opts_bin`, `raw_file_info_bin`, `read_multiple_req_bin`, and an element of `read_multiple_resps_bin` to the helper.

State and persistence: no runtime state or persistence. The important behavior is at compilation: generated prost field types must match the storage/node API zero-copy contract.

Dependencies and integration: depends on `bytes::Bytes` and `rustfs_protos::proto_gen::node_service` generated types. It protects storage RPC integration points that pass metadata blobs between disks or nodes.

Risks: this cannot validate wire compatibility or message contents; it only guards Rust field types. The repeated response case uses `first().cloned().unwrap_or_default()`, so it asserts the vector element type when present, not response population semantics.

Test signals: the test fails to compile if the generated protobuf configuration stops mapping the selected `bytes` fields to `Bytes`.
