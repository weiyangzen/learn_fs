# sources/storage-engines/foundationdb/bindings/go/CMakeLists.txt

## Purpose

This CMake file builds and tests the FoundationDB Go bindings inside the larger FoundationDB CMake build. It stages Go source files into a generated GOPATH layout, generates option/error binding files, compiles Go packages and the stack tester executable, and registers tests that verify generated checked-in files and gofmt cleanliness.

## Important APIs, Types, and Functions

`SRCS` lists the Go files copied into the build-local GOPATH, including binding packages, directory layer files, tests, and `go.mod`. `go_env` defines `GOPATH`, `CGO_CFLAGS`, `CGO_LDFLAGS`, and `GO111MODULE=auto`, making cgo point at the build tree’s C binding headers and libraries.

The local CMake function `build_go_package` parses `LIBRARY`, `EXECUTABLE`, `INCLUDE_TEST`, `NAME`, and `PATH`. It emits a `go install` custom command for either package archives or executables, creates an `ALL` custom target, and optionally builds a compiled Go test binary plus an `add_fdbclient_test` entry with the correct shared-library path.

Custom commands generate `src/fdb/generated.go` from `fdb.options` and `src/fdb/error_codes_generated.go` from Flow error definitions. `compare_files` tests ensure the generated build outputs match checked-in source copies.

## Control Flow

CMake first creates the GOPATH destination and a copy command for every source in `SRCS`. `copy_go_sources` materializes the staged tree. Generation targets depend on copied sources and run Go generator programs. Package targets are then declared in dependency order: `fdb_go`, `tuple_go`, `subspace_go`, `directory_go`, and `_stacktester` as `fdb_go_tester`. The final tests compare generated files and optionally run gofmt if found.

## State and Persistence Behavior

All generated and compiled artifacts are stored under `${CMAKE_CURRENT_BINARY_DIR}`. The source tree is not modified by the build; instead, generated output is compared against checked-in generated files. This gives CI a clear failure when source generators or upstream option/error definitions change without updating committed Go binding files.

## Dependencies and Integration Points

The file depends on a configured `GO_EXECUTABLE`, FoundationDB C binding target `fdb_c`, generated C binding headers, the build-tree `lib` directory, and CMake test helpers such as `add_fdbclient_test`. It integrates Go package compilation into the main FDB build graph while preserving the import path `github.com/apple/foundationdb/bindings/go/src`.

## Risks

The dependency in `build_go_package` references `${fdb_options_file}`, while the declared variable is `go_options_file`; if no variable alias exists externally, this can weaken dependency tracking. Platform mapping is hard-coded to `darwin_amd64`, `windows_amd64`, or `linux_amd64`, which may not match all Go build target names. The build uses GOPATH staging and `GO111MODULE=auto`, so behavior can vary with Go toolchain module defaults.

## Test Signals

Primary signals are successful `fdb_go`, `tuple_go`, `directory_go`, and `fdb_go_tester` targets, passing compiled Go package tests for `fdb` and `fdb/tuple`, passing generated-file compare tests, and a clean `fdb-go-fmt` test when `gofmt` is available.
