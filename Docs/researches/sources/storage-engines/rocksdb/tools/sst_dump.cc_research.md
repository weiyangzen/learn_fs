# sources/storage-engines/rocksdb/tools/sst_dump.cc

## Purpose
This is the executable entry point for the `sst_dump` tool. It constructs an `SSTDumpTool` and returns its `Run()` status.

## Important APIs, Types, and Functions
The only function is `main(int argc, char** argv)`, which includes `rocksdb/sst_dump_tool.h`, creates `ROCKSDB_NAMESPACE::SSTDumpTool tool`, and calls `tool.Run(argc, argv)`.

## Control Flow
All argument parsing, file traversal, and dumping logic is delegated to `SSTDumpTool::Run` in `sst_dump_tool.cc`.

## State and Persistence
This wrapper has no state of its own. Persistence side effects, such as raw dump output files, occur inside the tool implementation for selected commands.

## Dependencies and Integration Points
It links the standalone binary to the reusable `SSTDumpTool` class, allowing tests to call the same class directly without process spawning.

## Risks
There is minimal local risk. Any process initialization such as stack trace handlers or custom object registration must happen elsewhere if needed; this wrapper does not add it.

## Test Signals
`sst_dump_test.cc` tests `SSTDumpTool` directly. Process-level testing of this file is equivalent to invoking the compiled binary with help/version or SST inputs.
