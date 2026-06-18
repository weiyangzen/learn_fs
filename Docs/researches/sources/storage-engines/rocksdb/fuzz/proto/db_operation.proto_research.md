<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/fuzz/proto/db_operation.proto -->
# sources/storage-engines/rocksdb/fuzz/proto/db_operation.proto

## Purpose

`db_operation.proto` defines the protobuf-mutator input schema shared by RocksDB fuzzers that generate DB-like operations. It gives fuzzers structured operation sequences instead of raw byte interpretation.

## Important APIs, Types, and Functions

- `syntax = "proto2"` enables required fields and proto2 semantics.
- `enum OpType` defines `PUT`, `MERGE`, `DELETE`, and `DELETE_RANGE`.
- `message DBOperation` has required `key`, optional `value`, and required `type`.
- `message DBOperations` contains repeated `DBOperation operations`.

## Control Flow

There is no runtime control flow in the proto itself. Protobuf-mutator generates `DBOperations`; individual fuzzers post-process and interpret the sequence. `value` is used as a value for PUT/MERGE and as the end bound for DELETE_RANGE, while DELETE ignores it.

## State and Persistence Behavior

The schema represents transient fuzz input. Persistence is determined by harnesses that apply operations to RocksDB and generated C++ code under `fuzz/proto/gen`.

## Dependencies and Integration Points

It integrates with `fuzz/Makefile`'s `gen_proto` target, generated `db_operation.pb.cc/.h`, `db_map_fuzzer.cc`, and `sst_file_writer_fuzzer.cc`. The operation enum must stay aligned with each fuzzer's switch statements and post-processors.

## Risks and Edge Cases

The comment says `[key, value]` is the range for DELETE_RANGE, while fuzzer code treats it as `[key, value)`, matching RocksDB's API. Required fields can constrain mutator behavior and cause parsing failures for malformed serialized inputs. Adding enum values requires every harness to handle or intentionally reject them.

## Test Signals

Signals include successful proto generation, fuzzer builds after schema changes, post-processor compatibility, and harness behavior for every enum value including future unknown/default cases.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/fuzz/proto/db_operation.proto -->
