# sources/object-store/rustfs/crates/e2e_test/src/reliant/node_interact_test.rs

## sources/object-store/rustfs/crates/e2e_test/src/reliant/node_interact_test.rs

Purpose: ignored live-server tests for direct RustFS node-service gRPC interactions. The tests exercise lower-level cluster RPCs such as ping, volume operations, directory walking, file reads, and storage info.

Important APIs and functions: each test creates a `node_service_time_out_client` for `http://localhost:9000` with `TonicInterceptor::Signature(gen_tonic_signature_interceptor())`. `ping` constructs and decodes flatbuffer `PingBody`. `make_volume`, `list_volumes`, `read_all`, and `storage_info` call generated node-service RPCs. `walk_dir` serializes `WalkDirOptions` with MessagePack and consumes a streaming `WalkDirResponse` into `MetacacheWriter`/`MetacacheReader` via a Tokio duplex stream.

Control flow: tests are independent and ignored. `ping` validates the request flatbuffer then prints decoded response details. Volume tests send simple requests and print success/error or decoded `VolumeInfo`. `walk_dir` computes a disk path from `RUSTFS_DISK_PATH` or workspace target data, sends a `WalkDirRequest`, spawns one task to convert streaming JSON `MetaCacheEntry` responses into metacache format, and another to read/print entries. `read_all` prints response data for `format.json`; `storage_info` deserializes response bytes with `rmp_serde`.

State and persistence: server-side disk/volume state is external to the tests and addressed by disk names or filesystem paths. `make_volume` mutates the server by creating volume `dandan`. `walk_dir` reads from the configured data directory. No cleanup is performed.

Dependencies and integration points: RustFS ecstore RPC client, generated node-service protos, flatbuffers models, rmp-serde, filemeta metacache reader/writer, workspace test common path helper, tonic streaming, and Tokio tasks.

Risks: heavily environment-dependent and ignored. Hard-coded disk/volume names and lack of cleanup make tests unsuitable for isolated repeatability. Many assertions are weak or absent, with output printed for manual inspection. `walk_dir` unwraps JSON decoding in a spawned task and only joins tasks without inspecting panic results deeply.

Test signals: primarily smoke/manual diagnostics for signed node-service connectivity and serialization formats rather than strict automated assertions.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/reliant/node_interact_test.rs -->
