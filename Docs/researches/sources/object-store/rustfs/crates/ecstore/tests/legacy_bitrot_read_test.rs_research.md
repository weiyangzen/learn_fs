# sources/object-store/rustfs/crates/ecstore/tests/legacy_bitrot_read_test.rs

## Purpose

Integration test for reading legacy HighwayHash256S-protected object data through `create_bitrot_reader`, isolated from full ECStore object reads.

## Important APIs and Types

Uses `workspace_root`, `legacy_test_data_exists`, `run_legacy_bitrot_test_for_object`, `create_bitrot_reader`, `Endpoint`, `new_disk`, `STORAGE_FORMAT_FILE`, `get_file_info`, `FileInfoOpts`, and `HashAlgorithm::HighwayHash256SLegacy`.

## Control Flow

Skip logic checks `RUSTFS_SKIP_LEGACY_TEST` and fixture metadata. The helper reads `xl.meta`, parses file info with data included, rejects deleted/no-part objects, derives shard size and checksum info, switches to the legacy checksum algorithm when needed, then reads either inline data or local EC `part.1` through `create_bitrot_reader`.

## State and Persistence Behavior

Reads local fixture directories only and creates a disk abstraction with cleanup disabled. The documented env controls root/disk, but the test body currently hard-codes `/Users/weisd/project/minio` and disk `test`.

## Dependencies and Integration Points

Integrates bitrot readers, disk endpoint/local disk initialization, file metadata parsing, and legacy MinIO/RustFS fixture layout.

## Risks and Edge Cases

Hard-coded root/disk conflicts with documented environment variables and skip detection. It reads only `part.1` and asserts nonzero read rather than full content verification. Many failures return `false`, reducing assertion detail.

## Test Signals

Asserts `ktvzip.tar.gz` and `path_traversal.md` are readable, signaling compatibility with legacy checksum metadata, inline data, local part reads, and old `xl.meta` formats.
