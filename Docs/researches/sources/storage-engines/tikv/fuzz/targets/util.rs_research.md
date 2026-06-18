# sources/storage-engines/tikv/fuzz/targets/util.rs

## Purpose
Provides byte-reading helpers for fuzz targets, converting raw input streams into primitive Rust values with native-endian decoding.

## Important APIs, Types, and Functions
`ReadLiteralExt` extends any `io::Read` with `read_as_u8`, signed/unsigned 16/32/64-bit reads, `read_as_f64`, and `read_as_bool`. It delegates to `byteorder::ReadBytesExt` with `NativeEndian` for multi-byte primitives.

## Control Flow
Fuzz targets create a `Cursor<&[u8]>` and call these methods. Short input returns `io::Error`, which propagates through target `Result`s.

## State and Persistence Behavior
No persistent state. Reads advance the caller's stream position.

## Dependencies and Integration Points
Depends on `std::io` and `byteorder`. Used by `fuzz/targets/mod.rs` to keep target parsing concise.

## Risks
`NativeEndian` makes byte interpretation host-dependent, which can make corpora less reproducible across architectures. `read_as_bool` maps even bytes to true and odd bytes to false, which is simple but nonuniform only if fuzzer input distribution is biased.

## Test Signals
Unit-test primitive decoding on known byte arrays for supported platforms. Exercise short-input behavior and verify fuzz targets treat EOF as a non-crashing rejected case.
