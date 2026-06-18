# sources/object-store/rustfs/crates/checksums/src/error.rs

## Purpose
`error.rs` defines the public error type returned when a requested checksum algorithm name is not recognized.

## Important APIs, Types, and Functions
`UnknownChecksumAlgorithmError` stores the original algorithm string. `new` is crate-private and constructs the error. `checksum_algorithm` exposes the unknown value. `Display` renders a message listing accepted names: `crc32`, `crc32c`, `sha1`, `sha256`, and `md5`. It implements `std::error::Error`.

## Control Flow
The type is constructed by `ChecksumAlgorithm::from_str` in `lib.rs` when no case-insensitive match is found.

## State and Persistence Behavior
The only state is the owned algorithm string captured at parse time. No persistence.

## Dependencies and Integration Points
Integrated with Rust's `FromStr` trait for `ChecksumAlgorithm`; callers parsing algorithm strings can inspect the unknown value for diagnostics.

## Risks and Edge Cases
The display message includes `md5` as a known name even though parsing `md5` currently aliases to CRC32 instead of returning the deprecated `Md5` variant. If supported names change, this message must stay synchronized.

## Test Signals
`test_checksum_algorithm_returns_error_for_unknown` checks that the unknown string is preserved by `checksum_algorithm()`.
