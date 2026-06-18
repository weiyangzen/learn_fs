<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/dump/db_dump_tool.cc -->
# sources/storage-engines/rocksdb/tools/dump/db_dump_tool.cc

## Purpose
This file implements the binary dump and undump logic behind RocksDB's `rocksdb_dump` and `rocksdb_undump` tools. It serializes a read-only DB into a simple stream format and reconstructs a DB by reading that format and writing each key/value pair.

## Important APIs, Types, and Functions
- `DbDumpTool::Run(const DumpOptions&, Options)` opens a DB read-only and writes a dump file.
- `DbUndumpTool::Run(const UndumpOptions&, Options)` opens a dump file, validates it, opens or creates a DB, writes records, and optionally compacts.
- Dump format constants are `magicstr = "ROCKDUMP"` and an eight-byte version `{0,0,0,0,0,0,0,1}`.
- `EncodeFixed32()` and `DecodeFixed32()` serialize metadata length, key length, and value length.
- `Env::NewWritableFile()`, `Env::NewSequentialFile()`, `WritableFile::Append()`, `SequentialFile::Read()`, and `SequentialFile::Skip()` perform file I/O.

## Control Flow
Dumping opens the source DB with `create_if_missing=false`, opens the destination file, appends magic and version, emits either `{}` for anonymous dumps or JSON-like metadata containing absolute DB path, hostname, and creation time, then iterates the DB from first key to last. Each record is `uint32 key_size`, key bytes, `uint32 value_size`, and value bytes.

Undumping opens the sequential dump file, reads and validates magic and version, reads the info blob size and skips the metadata, opens the destination DB with `create_if_missing=true`, then loops reading key-size fields. A short or failed read of the next key-size ends the loop; short reads for key data, value size, or value data are treated as errors. Scratch buffers grow by doubling to accommodate large keys or values. Each record is inserted with `DB::Put()`. If requested, it compacts the full DB.

## State and Persistence Behavior
The dump file persists all key/value pairs visible through a default iterator in sorted order, plus optional metadata. It does not encode column families, snapshots, timestamps, sequence numbers, merges, deletes, range tombstones, blob-file identity, or DB options. Undump writes records into a live RocksDB DB path using caller-supplied options and can compact after loading.

## Dependencies and Integration Points
This implementation depends on `rocksdb/db_dump_tool.h` declarations, core `DB` and `Env` APIs, and RocksDB fixed-width coding helpers. It is invoked by the wrapper binaries in `rocksdb_dump.cc` and `rocksdb_undump.cc`, which parse gflags and options strings.

## Risks and Edge Cases
- Metadata JSON is built with `snprintf()` and does not escape strings; unusual path or hostname characters can produce invalid JSON-like text.
- The dump format has no checksum and limited validation. Truncation at a key-size boundary is treated as normal end-of-file.
- `DbDumpTool::Run()` checks iterator failure but prints `status.ToString()` instead of `it->status()`, so the reported status can be stale.
- Only the default column family is represented.
- Lengths are 32-bit; very large keys or values beyond that format are unsupported.

## Test Signals
There is no local unit test in this file. Signals are boolean return values, stderr messages on open/read/write/iteration/compaction failures, and successful round-trip use through `rocksdb_dump` and `rocksdb_undump`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/dump/db_dump_tool.cc -->
