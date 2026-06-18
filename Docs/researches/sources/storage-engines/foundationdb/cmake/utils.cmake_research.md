# sources/storage-engines/foundationdb/cmake/utils.cmake

## Purpose
Provides general CMake utility functions for source classification, path manipulation, source discovery, and gRPC/protobuf generation.

## Important APIs, Types, and Functions
Defines `is_header`, `remove_prefix`, `is_prefix`, `create_build_dirs`, `fdb_find_sources`, `package_name_to_path`, `package_name_to_proto_target`, and `generate_grpc_protobuf`.

## Control Flow and Integration
Flow build files use these helpers to prepare generated directories and collect sources. gRPC users call `generate_grpc_protobuf`, which creates a static target, sets include/link dependencies, invokes protobuf generation for `.pb` and `.grpc.pb` outputs, and marks generated files to skip linting.

## State and Persistence
Depends on Protobuf and gRPC CMake functions/targets and current source/binary directory context.

## Dependencies
State includes created build directories, generated protobuf sources under `${CMAKE_BINARY_DIR}/generated`, and CMake target properties.

## Risks and Test Signals
Risks include glob-based source discovery hiding new file types, absolute-path handling in `create_build_dirs`, and generated source target property assumptions. Test signals are target generation and successful protobuf/gRPC compilation.
