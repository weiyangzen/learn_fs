# sources/storage-engines/rocksdb/tools/blob_dump.cc

## Purpose

`blob_dump.cc` is the command-line entry point for inspecting RocksDB BlobDB/blob files through `BlobDumpTool`.

## Important APIs, Types, and Functions

It includes `utilities/blob_db/blob_dump_tool.h`, maps display strings `none`, `raw`, `hex`, and `detail` to `BlobDumpTool::DisplayType`, defines long options `--help`, `--file`, `--show_key`, `--show_blob`, `--show_uncompressed_blob`, and `--show_summary`, and calls `BlobDumpTool::Run`.

## Control Flow

`main` parses options with `getopt_long`. Help prints usage and exits. Optional display options without explicit values default blob/uncompressed blob display to hex, while keys default to raw. Invalid display types or unknown options return `-1`. After parsing, `BlobDumpTool tool; tool.Run(...)` performs the actual dump and returns success/failure.

## State and Persistence Behavior

The program reads the specified blob file and writes output to stdout/stderr. It does not mutate database state.

## Dependencies and Integration Points

It depends on libc `getopt`, C++ containers/strings, RocksDB `Status`, and `BlobDumpTool`. It integrates with RocksDB's tool build targets when included.

## Risks and Test Signals

Risks include not requiring `--file` before running, optional argument parsing quirks for short options, and returning `-1` instead of conventional positive exit codes. Signals are help output, invalid display-type errors, successful summary/detail/raw/hex dumps, and failure status for missing/corrupt files.
