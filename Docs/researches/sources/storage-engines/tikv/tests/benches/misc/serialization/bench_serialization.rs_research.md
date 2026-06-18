# sources/storage-engines/tikv/tests/benches/misc/serialization/bench_serialization.rs

Purpose: benchmarks protobuf serialization overhead for Raft log entries containing one or two TiKV `Put` requests. It focuses on the hot path of wrapping `kvproto::raft_cmdpb::RaftCmdRequest` inside `raft::eraftpb::Entry` and decoding it back.

Important APIs and functions: `gen_rand_str` creates random byte keys/values; `generate_requests` converts a borrowed byte-slice map into `Request` protobufs with `CmdType::Put` and CF `"tikv"`; `encode` serializes requests into `RaftCmdRequest`, then stores the bytes as `Entry.data`; `decode` merges bytes into `Entry` and then into `RaftCmdRequest`. Bench functions are `bench_encode_one`, `bench_decode_one`, `bench_encode_two`, and `bench_decode_two`.

Control flow: each bench pre-generates random input, builds a small `HashMap<&[u8], &[u8]>`, and measures only repeated encode or decode work inside `Bencher::iter`. Decode cases precompute encoded data once.

State and persistence: no durable state is written. The simulated persisted object is a Raft `Entry` byte vector, exercising allocation and protobuf message layout.

Dependencies and integration: depends on `kvproto`, `protobuf::Message`, `raft`, `rand`, `collections::HashMap`, and Rust unstable `test` benches. It integrates with the misc serialization bench module.

Risks and test signals: map iteration order is non-deterministic, so this measures average serialization cost rather than stable wire ordering. `unwrap()` is acceptable in benchmarks but hides malformed data behavior. Signal is performance regression in request serialization size/count scenarios.
