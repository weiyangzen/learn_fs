<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/fuzz/sst_file_writer_fuzzer.cc -->
# sources/storage-engines/rocksdb/fuzz/sst_file_writer_fuzzer.cc

## Purpose

`sst_file_writer_fuzzer.cc` is a protobuf-mutator harness that drives `SstFileWriter` with sorted unique operations, opens the generated SST through the internal table reader path, verifies checksums, and checks internal keys and values. It targets table-builder/SST writer correctness, internal-key encoding, and table-reader compatibility.

## Important APIs, Types, and Functions

- A `PostProcessorRegistration<DBOperations>` normalizes range bounds, sorts operations by key, and removes duplicate keys to satisfy `SstFileWriter`'s sorted-unique key requirement.
- `NewTableReader()` mirrors `SstFileReader::Open`: gets file size, creates `RandomAccessFileReader`, builds `TableReaderOptions`, and calls the table factory.
- `ToValueType(OpType)` maps proto operations to RocksDB internal value types.
- `DEFINE_PROTO_FUZZER(DBOperations& input)` writes the SST and verifies it.
- APIs include `SstFileWriter::Open/Put/Merge/Delete/DeleteRange/Finish`, `TableReader::VerifyChecksum`, `TableReader::NewIterator`, `ParseInternalKey`, and filesystem test directory lookup.

## Control Flow

The post-processor first ensures each DELETE_RANGE has ordered bounds, then sorts all operations by user key and erases duplicate-key operations. The fuzzer gets a test directory, writes a fixed SST filename, constructs default `Options`, `EnvOptions`, and `ImmutableCFOptions`, opens an `SstFileWriter`, applies every operation, and finishes the file. It then opens the generated table with a `TableReader`, verifies full-file checksums, creates an internal iterator with filters skipped, and walks expected operations. DELETE_RANGE entries are skipped because this iterator path does not expose range tombstone entries. For other operations it parses the internal key, checks user key, sequence zero, value type, and value when applicable. Finally it removes the SST file.

## State and Persistence Behavior

The harness creates one SST file in the filesystem test directory and deletes it at the end. It does not create a DB. The SST contains sequence-zero external file entries and possibly range-deletion metadata. Persistent state under test is the table file's on-disk block/index/filter/checksum/internal-key representation.

## Dependencies and Integration Points

It depends on generated proto classes, protobuf-mutator, `SstFileWriter`, table reader/builder internals, default table factory, `RandomAccessFileReader`, internal key parsing, comparators, and `util.h` check macros. It exercises public external-SST writing and internal table-reader validation in one harness.

## Risks and Edge Cases

The fixed filename in the test directory can collide under parallel fuzzing. Duplicate-key erasure keeps the first operation after sort, which may reduce coverage of overwrite-like cases but is required by writer ordering constraints. DELETE_RANGE output is only indirectly covered by `Finish()` and checksum verification because normal internal iteration skips range tombstones. `TableReaderOptions` passes a null compression manager and default options, so custom compression paths are not covered.

## Test Signals

Signals include aborts from writer/table status failures, checksum verification failures, internal-key parse errors, key/type/value mismatches, sanitizer findings, and leftover SST files after crashes. Good corpora should cover all operation types, empty keys/values, adjacent range bounds, and large value payloads.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/fuzz/sst_file_writer_fuzzer.cc -->
