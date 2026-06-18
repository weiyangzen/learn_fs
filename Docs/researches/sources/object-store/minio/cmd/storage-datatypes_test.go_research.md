# sources/object-store/minio/cmd/storage-datatypes_test.go

## Purpose

`storage-datatypes_test.go` contains hand-written benchmarks for selected storage datatype serialization paths. Unlike the generated test file, this file compares msgp performance with Go gob for representative values and includes a populated `FileInfo` with realistic object metadata, erasure layout, encryption-related metadata keys, part metadata, checksums, and timestamps.

## Important APIs, Types, And Functions

The benchmark set covers:

- `BenchmarkDecodeVolInfoMsgp`, which decodes a msgp-encoded `VolInfo`.
- `BenchmarkDecodeDiskInfoMsgp` and `BenchmarkEncodeDiskInfoMsgp`, which measure msgp on a populated `DiskInfo`.
- `BenchmarkDecodeDiskInfoGOB` and `BenchmarkEncodeDiskInfoGOB`, which provide gob baselines for the same `DiskInfo`.
- `BenchmarkDecodeFileInfoMsgp` and `BenchmarkEncodeFileInfoMsgp`, which measure msgp on a complex `FileInfo`.
- `BenchmarkDecodeFileInfoGOB` and `BenchmarkEncodeFileInfoGOB`, which provide gob baselines for that complex `FileInfo`.

The benchmarks use `msgp.Encode`, `msgp.NewEndlessReader`, `msgp.NewReader`, `gob.NewEncoder`, `gob.NewDecoder`, `io.Discard`, `bytes.Buffer`, `time.Now`, and MinIO's `UTCNow()`.

## Control Flow

Each decode benchmark builds a value, encodes it once into a `bytes.Buffer`, logs the encoded size, configures allocation reporting and byte accounting, then repeatedly decodes from a reusable endless reader. Gob decode benchmarks keep the encoded byte slice and create a new `bytes.Buffer` and decoder each iteration. Encode benchmarks write to `io.Discard`, using either `msgp.Encode` or a reusable gob encoder.

The file uses `b.Loop()` loops, so benchmark execution depends on a Go toolchain that supports that testing API. There are no assertions outside fataling on encode/decode errors.

## State And Persistence Behavior

No persistent state is created. The benchmark values model storage-layer state: `DiskInfo` contains capacity and endpoint data; `FileInfo` models object version metadata, encryption metadata, part information, erasure coding parameters, distribution, and checksum records. The realistic `FileInfo` payload is important because metadata maps and nested slices dominate object metadata serialization cost.

## Dependencies And Integration Points

This file depends on standard-library `bytes`, `encoding/gob`, `io`, `testing`, and `time`, plus `github.com/tinylib/msgp/msgp`. It integrates with storage datatype definitions and generated msgp methods from the same package.

The practical integration signal is performance rather than correctness. These benchmarks justify and monitor the generated msgp path used by storage REST/grid calls and metadata movement.

## Risks

The benchmarks are not unit tests and will not fail on performance regressions unless a separate benchmark comparison process is used. They cover only a few representative values, so they do not exercise all generated datatypes, nil edge cases, omitted fields, tuple arity failures, or decode compatibility with older wire formats.

The gob comparison may not match production behavior, because production storage RPCs use msgp. It is useful as a relative baseline but should not be interpreted as a protocol compatibility test.

## Test Signals

Running these benchmarks provides allocation and throughput signals for `VolInfo`, `DiskInfo`, and `FileInfo` serialization. The generated test file remains the broader smoke-test signal for every generated codec.
