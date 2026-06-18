# sources/object-store/minio/cmd/metacache_gen_test.go

Purpose: This generated test file validates the msgp serialization implementation for the `metacache` struct and benchmarks generated methods.

Important APIs and types: It uses `metacache`, generated `MarshalMsg`, `UnmarshalMsg`, `EncodeMsg`, `DecodeMsg`, `Msgsize`, and msgp utilities for skip, stream encode/decode, writer, reader, and endless reader benchmarking.

Control flow: `TestMarshalUnmarshalmetacache` marshals a zero-value cache, unmarshals it, checks no bytes remain, and verifies `msgp.Skip` consumes the payload. `TestEncodeDecodemetacache` encodes to a buffer, warns if `Msgsize` is too small, decodes into a new value, and verifies reader skip. Benchmarks cover marshal, append marshal, unmarshal, encode, and decode.

State and persistence behavior: The tests operate entirely in memory with zero-value `metacache`. They do not create cache-manager entries, remote updates, or `.metacache` block objects.

Dependencies and integration points: These tests protect the generated binary format used by metacache managers and peer coordination. They are most useful as generator/runtime compatibility checks.

Risks: Like the other generated tests, this suite does not assert populated timestamps, status values, IDs, or error strings round-trip. It also does not cover unknown numeric `scanStatus` values or mixed-version payloads.

Test signals: Passing signals are error-free marshal/unmarshal, no remaining bytes, successful skip, successful stream decode, and stable benchmark behavior.
