<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/fuzz/Makefile -->
# sources/storage-engines/rocksdb/fuzz/Makefile

## Purpose

`fuzz/Makefile` builds RocksDB's libFuzzer targets under either a local sanitizer environment or OSS-Fuzz. It wires protobuf/libprotobuf-mutator code generation, RocksDB include/library paths, sanitizer flags, and target-specific build rules for DB and SST fuzzers.

## Important APIs, Types, and Functions

- `ROOT_DIR` points at the RocksDB root and includes `make_config.mk`.
- `PROTOBUF_CFLAGS/LDFLAGS` and `PROTOBUF_MUTATOR_CFLAGS/LDFLAGS` come from `pkg-config`.
- `PROTO_IN` is `fuzz/proto`; `PROTO_OUT` is `fuzz/proto/gen`.
- `FUZZ_ENV=ossfuzz` switches from local `-fsanitize=address,fuzzer` flags to OSS-Fuzz-provided `CXXFLAGS` and `LIB_FUZZING_ENGINE`.
- `PROTOC_BIN` is configurable for `gen_proto`.
- Targets: `gen_proto`, `clean`, `db_fuzzer`, `db_map_fuzzer`, and `sst_file_writer_fuzzer`.

## Control Flow

For non-OSS-Fuzz builds the file sets `CC=$(CXX)`, adds ASan/libFuzzer flags, includes RocksDB root/include/proto output paths, links protobuf-mutator/protobuf and `-lrocksdb`. In OSS-Fuzz mode it respects externally supplied compiler and sanitizer flags while still adding generated proto and RocksDB includes. `gen_proto` creates the output directory and runs `protoc` over all proto inputs. The proto-based fuzzers depend on generated code and compile `proto/gen/db_operation.pb.cc` into the target.

## State and Persistence Behavior

The Makefile creates generated C++ protobuf files under `fuzz/proto/gen` and fuzzer binaries in the fuzz directory. `clean` removes the three fuzzer binaries and generated proto output. It does not modify source files outside generated artifacts.

## Dependencies and Integration Points

It depends on RocksDB's built `librocksdb`, `pkg-config`, protobuf, libprotobuf-mutator, libFuzzer-compatible compiler support, and `make_config.mk` platform flags. It integrates with OSS-Fuzz by consuming its standard environment variables and with local developer fuzzing via default sanitizer flags.

## Risks and Edge Cases

If RocksDB has not been built or `pkg-config` cannot find protobuf/libprotobuf-mutator, targets fail at compile/link time. The local mode hardcodes ASan plus libFuzzer, which may not suit all compiler setups. Generated proto paths are included as `-I$(PROTO_OUT)`, so stale generated files can mask proto changes unless `gen_proto` reruns. `clean` removes generated proto output wholesale.

## Test Signals

Signals include `make -C fuzz gen_proto`, successful builds of all three fuzzers in local mode, successful OSS-Fuzz environment builds, correct regeneration after proto edits, and fuzzer startup without missing RocksDB/protobuf symbols.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/fuzz/Makefile -->
