# sources/storage-engines/foundationdb/fdbctl/CMakeLists.txt

## Purpose
This build file defines the `fdbctl` static library target and optional gRPC/protobuf generation for the FoundationDB control service.

## Important APIs, Types, And Functions
It uses `fdb_find_sources(FDBCTL_SRCS)`, `add_flow_target(STATIC_LIBRARY NAME fdbctl SRCS ...)`, `target_include_directories`, `target_link_libraries`, conditional `generate_grpc_protobuf`, and a UBSAN link option.

## Control Flow
CMake discovers sources, creates the static library, exposes the `include` directory, links privately to `fdbclient`, and, when `WITH_GRPC` is enabled, generates protobuf/gRPC code from `protos/control_service.proto` and links it publicly. Under `USE_UBSAN`, it adds `-rdynamic`.

## State And Persistence Behavior
The file controls build artifacts only: a static library and generated protobuf sources/targets. It has no runtime state.

## Dependencies And Integration Points
The target integrates with the Flow build macros, FoundationDB client library, and optional gRPC/protobuf toolchain. Consumers need `WITH_GRPC` for the control service sources guarded by `FLOW_GRPC_ENABLED`.

## Risks And Edge Cases
When Go/grpc/protobuf generation settings change, generated target names must remain aligned with includes such as `fdbctl/control_service/control_service.pb.h`. If `WITH_GRPC` is off, much of the fdbctl C++ service code is compiled out.

## Test Signals
Build signals are successful `fdbctl` target creation with and without `WITH_GRPC`, generated proto headers available in include paths, and UBSAN builds linking with symbols.
