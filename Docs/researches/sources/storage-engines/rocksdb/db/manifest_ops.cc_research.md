<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/manifest_ops.cc -->
# sources/storage-engines/rocksdb/db/manifest_ops.cc

## Purpose
Implements `GetCurrentManifestPath()`, a small helper that reads a RocksDB `CURRENT` file, validates it, parses the referenced manifest file number, and returns the absolute manifest path under the DB directory.

## Important APIs, Types, And Functions
`GetCurrentManifestPath(const std::string& dbname, FileSystem* fs, bool is_retry, std::string* manifest_path, uint64_t* manifest_file_number)` is the only function. It uses `ReadFileToString()`, `CurrentFileName(dbname)`, and `ParseFileName()` from filename utilities. When `is_retry` is true, it sets `IOOptions::verify_and_reconstruct_read` before reading.

## Control Flow
The function asserts non-null filesystem and output pointers, constructs IO options, reads the `CURRENT` file contents, and returns any read error. It then requires the contents to be non-empty and newline-terminated, strips the newline, parses the filename into a number and type, requires `kDescriptorFile`, and builds `manifest_path` as `dbname + "/" + fname` unless `dbname` already ends with `/`.

## State And Persistence Behavior
It only reads persistent DB metadata. It does not modify `CURRENT` or the manifest. The returned manifest path and file number become inputs to version-set recovery or retry paths. With `is_retry`, the filesystem may perform stronger integrity verification/reconstruction reads.

## Dependencies And Integration Points
Depends on `db/manifest_ops.h` and `file/filename.h`. Integrates with DB open/recovery code that needs to locate the active MANIFEST from `CURRENT`, especially after a perceived corruption where retry reads should be more defensive.

## Risks And Edge Cases
Malformed `CURRENT` files produce corruption statuses if missing the trailing newline, empty, unparsable, or not naming a descriptor file. `dbname.back()` assumes `dbname` is non-empty. The helper does not normalize paths beyond inserting a slash, so callers control DB path canonicalization.

## Test Signals
Relevant tests should cover valid `CURRENT`, missing newline, empty content, non-MANIFEST filename, parse failures, read errors, retry mode setting `verify_and_reconstruct_read`, and DB names with and without trailing slash.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/manifest_ops.cc -->
