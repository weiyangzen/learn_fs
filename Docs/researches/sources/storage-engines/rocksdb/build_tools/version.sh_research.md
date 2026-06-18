# sources/storage-engines/rocksdb/build_tools/version.sh

## Purpose
This Bash helper prints RocksDB version components from `include/rocksdb/version.h`. It supports release scripts and build tooling that need `major`, `minor`, `patch`, or full semantic version text.

## Important APIs, functions, and control flow
The script requires one argument and prints usage for no arguments. For `major`, `minor`, and `patch`, it greps the first matching macro line and prints the third token with awk. For `full`, it scans `#define ROCKSDB...` lines into an awk map and prints `ROCKSDB_MAJOR.ROCKSDB_MINOR.ROCKSDB_PATCH`.

## State, persistence, and dependencies
It is read-only and depends on being run from the repository root or another working directory where `include/rocksdb/version.h` resolves. It depends on `grep`, `head`, and `awk`.

## Integration points
Release packaging, Docker tagging, or build scripts can call it as `build_tools/version.sh full` or one component at a time. It uses the public version header as the source of truth.

## Risks and test signals
Unknown arguments silently produce no output but exit 0, which can mask caller mistakes. Grep patterns are broad and could match unexpected macro names if the header changes. Test by comparing all four outputs to `include/rocksdb/version.h` and checking caller behavior on invalid arguments.
