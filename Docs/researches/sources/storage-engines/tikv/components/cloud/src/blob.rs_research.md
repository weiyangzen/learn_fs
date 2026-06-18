# sources/storage-engines/tikv/components/cloud/src/blob.rs

## Purpose
Defines shared blob-storage abstractions and helpers used by provider crates. It decouples cloud providers from external storage internals while providing common config URL handling, object listing types, non-empty string validation, and optimized async read-to-end behavior.

## Important APIs, Types, And Functions
- `BlobConfig` exposes provider name and display URL.
- `PutResource<'a>` wraps a boxed async reader for uploads and implements `AsyncRead`.
- `BlobStream<'a>` is a boxed async reader for downloads.
- `BlobStorage` defines async `put` and streaming `get`/`get_part`.
- `DeletableStorage` and `IterableStorage` define optional delete and prefix iteration contracts.
- `unimplemented` returns `Unsupported` `io::Error` with caller location.
- `StringNonEmpty`, `BucketConf`, `none_to_empty`, and `read_to_end` provide shared config and buffering utilities.

## Control Flow
Provider configs construct `BucketConf` and implement `BlobConfig::url` by delegating to `BucketConf::url`. Storage callers use trait objects for provider-specific implementations. `read_to_end` performs `futures::io::copy` into a `Cursor<&mut Vec<u8>>`, avoiding repeated initialization behavior in `AsyncReadExt::read_to_end`.

## State And Persistence Behavior
This file has no persistence. Its types describe provider state and data streams. `StringNonEmpty` enforces non-empty config at construction time; `BucketConf::url` percent-encodes path components through `url::Url`.

## Dependencies And Integration Points
Used by Azure, GCP, AWS, and external storage integrations. Depends on `async_trait`, `futures`, `futures_io`, `url`, and standard IO/pin/panic location APIs.

## Risks And Edge Cases
`StringNonEmpty` treats whitespace-only strings as non-empty. `BucketConf::url` overwrites endpoint paths with `bucket/prefix`, which is intended for custom endpoints but can surprise callers. `unimplemented` exposes caller source location in errors. `read_to_end` still buffers complete streams.

## Test Signals
Tests cover bucket URL generation with and without endpoints and benchmark `read_to_end` against standard futures behavior using a throttled reader. Benchmarks require nightly `test` and are not ordinary unit assertions except internal length checks.
