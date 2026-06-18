# sources/storage-engines/rocksdb/file/read_write_util.h

## Purpose

`read_write_util.h` declares low-level read/write helper APIs for RocksDB's file layer: writable-file creation, fallback file-size lookup, and debug-only sector alignment checks.

## Important APIs, Types, and Functions

- `NewWritableFile(FileSystem*, const std::string&, std::unique_ptr<FSWritableFile>*, const FileOptions&)`.
- `enum class FileSizeFallback` with `kNotSupportedOnly` and `kAnyOpenFileError`.
- `using BeforePathFileSizeFallback = void (*)()`.
- `GetFileSizeFromOpenFileOrPath(...)`.
- Debug-only `IsFileSectorAligned(...)`.

## Control Flow and State

The header declares stateless utilities. The file-size API encodes a two-stage strategy: prefer an open random-access file, then use path lookup according to fallback policy. It exposes a callback hook before path fallback without tying callers to a particular callback object type.

## Dependencies and Integration Points

It includes `sequence_file_reader.h`, `rocksdb/env.h`, and `rocksdb/file_system.h`. The helpers are used by file wrappers, readahead code, and tests needing consistent RocksDB filesystem behavior.

## Risks and Edge Cases

- The callback type is a raw function pointer, so capturing lambdas cannot be passed directly.
- Callers must pass non-null file, filesystem, and output size pointers.
- The debug-only alignment function should not be used as the only production validation.

## Test Signals

Coverage is indirect through readahead direct-buffer assertions and file-creation fault-injection tests. File-size fallback behavior should be covered with mock filesystems that return `NotSupported` and other errors.
