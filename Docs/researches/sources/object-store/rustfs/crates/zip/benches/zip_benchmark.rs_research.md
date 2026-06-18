# sources/object-store/rustfs/crates/zip/benches/zip_benchmark.rs

## Purpose
Provides Criterion benchmarks for tar-family extraction, zip creation/extraction round trips, extraction hotspot breakdowns, and object-archive extraction scenarios.

## Important APIs, Types, And Functions
`build_runtime` creates a current-thread Tokio runtime. `build_tar_payload` builds in-memory tar data through a duplex stream; `build_compressed_tar_payload` compresses it with `rustfs_zip::Compressor`. `bench_tar_family_extract` benchmarks gzip/zstd tar extraction with callback counting. `bench_zip_helper_round_trip` creates and extracts matrices of flat/nested/deep zip files. `bench_zip_helper_hotspot_breakdown` isolates tempdir setup, zip creation, zip extraction, summary-only extraction, raw `zip::ZipArchive` reading, and file-write costs. `build_object_archive_files` constructs synthetic object metadata/payload layouts. `bench_zip_object_archive_extract` benchmarks full and summary-only extraction for metadata-heavy and mixed archives.

## Control Flow And State
Benchmarks build deterministic payload vectors, use temp directories per iteration to isolate filesystem side effects, and wrap result counts/byte totals in `black_box`. Async crate APIs are driven through `runtime.block_on`. Atomic counters are used for tar callback counts.

## Dependencies And Integration Points
Depends on Criterion, `rustfs_zip` public APIs, `tempfile`, `tokio_tar`, and the upstream `zip` crate. It is registered by the crate manifest and provides performance visibility for archive helper APIs.

## Risks And Test Signals
The benchmark measures tempdir and filesystem overhead as part of several cases; the hotspot group intentionally breaks this down. Payloads are synthetic repeated bytes, so compression ratios may not reflect real object data. Bench assertions validate enclosed names and entry size limits in the reader-only path, but this is performance coverage rather than correctness testing.
