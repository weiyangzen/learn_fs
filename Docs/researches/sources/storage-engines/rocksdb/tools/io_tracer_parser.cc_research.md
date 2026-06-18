<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/io_tracer_parser.cc -->
# sources/storage-engines/rocksdb/tools/io_tracer_parser.cc

## Purpose
This file is the minimal `main()` wrapper for the IO trace parser tool. It either delegates to `ROCKSDB_NAMESPACE::io_tracer_parser()` when gflags is available or reports that gflags is required.

## Important APIs, Types, and Functions
- gflags-disabled `main()` prints an error and returns one.
- gflags-enabled `main(int argc, char** argv)` includes `tools/io_tracer_parser_tool.h` and returns `io_tracer_parser(argc, argv)`.

## Control Flow
Compilation is split by `#ifndef GFLAGS`. In supported builds, all command parsing and record processing is handled by `io_tracer_parser_tool.cc`; this wrapper only forwards arguments and returns its status.

## State and Persistence Behavior
The wrapper owns no persistent state. State behavior is entirely in the parser implementation and the trace file it reads.

## Dependencies and Integration Points
The file integrates the reusable parser function with a standalone executable target. Its only implementation dependency under gflags is `tools/io_tracer_parser_tool.h`.

## Risks and Edge Cases
The only notable risk is build configuration: without gflags the tool cannot function and exits with an error. Runtime validation of `--io_trace_file` is delegated.

## Test Signals
The wrapper participates in `io_tracer_parser_test.cc` indirectly through the same parser function. Manual signal is the executable's exit code.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/io_tracer_parser.cc -->
