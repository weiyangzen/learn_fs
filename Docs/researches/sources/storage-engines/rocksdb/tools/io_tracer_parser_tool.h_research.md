<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/io_tracer_parser_tool.h -->
# sources/storage-engines/rocksdb/tools/io_tracer_parser_tool.h

## Purpose
This header declares the reusable IO trace parser API used by both the standalone parser binary and tests. It exposes `IOTraceRecordParser` and the `io_tracer_parser()` entry function.

## Important APIs, Types, and Functions
- Forward declarations: `IOTraceHeader` and `IOTraceRecord`.
- `class IOTraceRecordParser` stores an input file path and exposes `ReadIOTraceRecords()`.
- Private formatting helpers are `PrintHumanReadableHeader()` and `PrintHumanReadableIOTraceRecord()`.
- `int io_tracer_parser(int argc, char** argv)` is the CLI-compatible parser entry point.

## Control Flow
The header only declares control flow. The expected flow is construction with a binary input file, `ReadIOTraceRecords()` opening and walking records, and private print helpers formatting the header and records.

## State and Persistence Behavior
The only class state is `input_file_`, the path of the binary trace file. The parser does not own persistent output state at the type level.

## Dependencies and Integration Points
The header includes `rocksdb/env.h` and `rocksdb/status.h`, though the public declarations mostly need standard string support through included RocksDB headers. It is included by `io_tracer_parser.cc`, `io_tracer_parser_tool.cc`, and `io_tracer_parser_test.cc`.

## Risks and Edge Cases
- The private helper comments mention dumping records in `output_file_`, but the class has no output-file member; implementation prints to stdout. This stale comment can mislead users.
- Including heavier RocksDB headers in a small interface increases compile coupling.
- Because the CLI function is declared unconditionally but implemented only under gflags in the `.cc`, build targets must align compile definitions.

## Test Signals
The header has no standalone tests. Its declarations are exercised by the parser binary wrapper and the IO tracer parser gtest.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/io_tracer_parser_tool.h -->
