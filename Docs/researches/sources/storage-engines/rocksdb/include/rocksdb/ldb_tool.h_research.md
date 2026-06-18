# Research: sources/storage-engines/rocksdb/include/rocksdb/ldb_tool.h

## Purpose

`ldb_tool.h` declares the embeddable public interface for RocksDB's `ldb` command-line tool. It lets the standalone `tools/ldb.cc` binary and external callers run ldb commands with supplied DB options, column-family descriptors, and custom display formatting.

## Important APIs, Types, and Functions

The header exposes `SliceFormatter`, `LDBOptions`, and `LDBTool`. `SliceFormatter::Format` converts raw `Slice` keys to readable strings. `LDBOptions` carries a shared `key_formatter` and `print_help_header`, defaulting to `"ldb - RocksDB Tool"`. `LDBTool::Run` is deprecated because it exits the process. `LDBTool::RunAndReturn` executes command parsing and returns an integer status.

## Control Flow

`tools/ldb.cc` constructs `LDBTool` and calls into this interface. The implementation in `tools/ldb_tool.cc` delegates to `LDBCommandRunner::RunCommand`, which prints help or version for short invocations, creates a concrete `LDBCommand` from argv, validates command-line options, runs the command, emits command execution text to stderr, deletes the command object, and returns 0 or 1. `Run` simply calls `exit(RunAndReturn(...))`.

## State and Persistence Behavior

The header stores no durable state itself. Commands behind the interface can open DBs, read or mutate keys, write external SSTs, update manifests, repair, backup, restore, checkpoint, ingest files, and inspect metadata. The supplied `Options` and optional column-family descriptors control DB open behavior.

## Dependencies and Integration Points

It depends on `rocksdb/db.h` and `rocksdb/options.h`. Implementation integrates with `rocksdb/utilities/ldb_cmd.h` and `tools/ldb_cmd_impl.h`. Build files expose `ldb`, `ldb_cmd_test`, and Python `tools/ldb_test.py`. HISTORY entries show ldb is a compatibility and operations surface for blob files, wide columns, file checksums, secondary/follower opens, option loading, unsafe metadata repair, and consistency checks.

## Risks and Edge Cases

Using deprecated `Run` from libraries can terminate the host process and trigger leak reports because default options are not unwound. `SliceFormatter` affects display only; command behavior must not depend on formatted keys unless explicitly wired by command code. ldb commands can perform dangerous persistence operations such as manifest updates and unsafe SST removal, so options validation and clear exit codes matter. Option loading from copied DBs has historically been subtle around `wal_dir`.

## Test Signals

Primary signals are `tools/ldb_cmd_test.cc`, `tools/ldb_test.py`, shell scripts using `ldb scan`, and HISTORY regressions for wide-column dump/scan, blob checksum output, option loading, compression support errors, and consistency checks. For embedders, `RunAndReturn` exit status and stderr execution result are the key observable signals.
