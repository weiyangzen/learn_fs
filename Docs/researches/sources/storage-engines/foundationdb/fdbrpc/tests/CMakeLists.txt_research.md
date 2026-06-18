# sources/storage-engines/foundationdb/fdbrpc/tests/CMakeLists.txt

## Purpose
This CMake file wires fdbrpc test and benchmark targets into the build. It conditionally builds and registers the TLS authorization unit test, conditionally generates gRPC/protobuf code for the echo proto, and always builds the fdbrpc transport benchmark.

## Important APIs, Types, And Functions
The file uses project CMake helpers `add_flow_target` and `generate_grpc_protobuf`. It defines executable targets `authz_tls_unittest` and `fdbrpc_transport_bench`, links them to project libraries, and registers CTest test `authorization_tls_unittest` when `OPEN_FOR_IDE` is false.

## Control Flow
On non-Windows platforms, `authz_tls_unittest` is built from `AuthzTlsTest.cpp` and linked with `flow`, `fdbrpc`, and `fmt::fmt`. If not generating IDE-only projects, it is added as a CTest test with `TIMEOUT 120`. If `WITH_GRPC` is enabled, protobuf/gRPC sources are generated from `protos/echo.proto`. Finally, `fdbrpc_transport_bench` is built from `fdbrpc_bench.cpp` and linked with `flow`, `fdbrpc`, and Boost program options.

## State And Persistence Behavior
The file itself does not manage runtime state. Its build state is expressed through generated targets, test registrations, and optional generated protobuf outputs controlled by `WITH_GRPC`.

## Dependencies And Integration Points
It integrates fdbrpc tests with CTest, the Flow target macro system, the project's gRPC generation helper, `fmt`, Boost program options, and platform conditionals. The TLS test target depends on POSIX behavior and is therefore excluded on Windows.

## Risks And Test Signals
Because the benchmark target is always added, builds must provide Boost program options even when only tests are desired. The authorization test is omitted under `OPEN_FOR_IDE`, so IDE project generation will not expose the CTest signal. gRPC code generation is conditional; users expecting echo service generated code must enable `WITH_GRPC`. CTest should show `authorization_tls_unittest` on non-Windows non-IDE builds, and target creation should be checked with `WITH_GRPC` both on and off.
