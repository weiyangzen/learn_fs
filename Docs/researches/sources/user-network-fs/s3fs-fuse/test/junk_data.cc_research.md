# sources/user-network-fs/s3fs-fuse/test/junk_data.cc

## Purpose
Fast deterministic data generator used by integration tests instead of slower random data sources.

## Important APIs, Types, And Control Flow
`main` expects a byte count, allocates a 128 KiB stack buffer, fills it with incrementing `uint64_t` patterns based on output offset, and writes chunks to stdout until the requested byte count is produced.

## State And Persistence
No persistent state. It streams bytes to stdout for callers to redirect into local or mounted files.

## Dependencies And Integration Points
Depends on C stdio/stdlib and integer types. Called throughout `integration-test-main.sh` to produce large files for multipart, cache, sparse, and concurrency tests.

## Risks And Test Signals
No error checking on `fwrite`, no validation for invalid numeric input beyond `strtoull`, and reinterpret-casting a char buffer to `uint64_t*` may raise strict-aliasing/alignment concerns on unusual platforms. Its deterministic output makes `cmp`-based integration tests reliable.
