<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/io_tracer_parser_test.cc -->
# sources/storage-engines/rocksdb/tools/io_tracer_parser_test.cc

## Purpose
This GoogleTest suite validates the IO trace parser by generating actual RocksDB IO trace files, invoking `io_tracer_parser()` in-process, and checking start/end tracing boundaries.

## Important APIs, Types, and Functions
- `IOTracerParserTest` fixture creates a per-thread test directory, trace file path, DB path, and a RocksDB DB with `create_if_missing=true`.
- `GenerateIOTrace()` creates a `TraceWriter`, calls `DB::StartIOTrace()`, performs ten Put+Flush operations, ends tracing with `DB::EndIOTrace()`, and verifies the trace file exists.
- `RunIOTracerParserTool()` builds an argv buffer containing `./io_tracer_parser` and `-io_trace_file=<path>`, then asserts `io_tracer_parser(argc, argv) == 0`.
- Tests are `InvalidArguments`, `DumpAndParseIOTraceRecords`, `NoRecordingAfterEndIOTrace`, and `NoRecordingBeforeStartIOTrace`.

## Control Flow
The fixture opens the DB at construction and destroys it plus the trace file and test directory in the destructor. `InvalidArguments` calls the parser without the required flag and expects failure. The dump/parse test generates a trace and parses it. The end-boundary test records trace file size after `EndIOTrace()`, performs more writes and flushes, and asserts the trace file size is unchanged. The before-start test writes and flushes before starting tracing and asserts no trace file exists, then generates and parses a trace.

## State and Persistence Behavior
The tests create real RocksDB data and real binary IO trace files under a per-thread temp directory. Trace file size is used as a persistence signal for whether operations after `EndIOTrace()` were recorded. DB teardown calls `DestroyDB()` with the fixture Env and deletes the test path.

## Dependencies and Integration Points
The suite depends on gflags, GoogleTest, RocksDB DB APIs, trace reader/writer APIs, `test_util`, and `tools/io_tracer_parser_tool.h`. Without gflags it builds a `main()` that reports the missing dependency and returns zero, effectively skipping the suite.

## Risks and Edge Cases
- Tests assert parser success but do not validate exact human-readable stdout.
- Trace generation relies on Put+Flush producing IO records on the current Env.
- The argv-building helper uses fixed-size buffers and repeats code from the invalid-argument test.
- File-size equality after `EndIOTrace()` is a coarse but useful boundary check.

## Test Signals
Passing tests confirm required argument validation, successful parsing of a generated trace, no recording before `StartIOTrace()`, and no recording after `EndIOTrace()`. The gtest `main()` installs the RocksDB stack trace handler.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/io_tracer_parser_test.cc -->
