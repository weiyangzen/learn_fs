# sources/storage-engines/foundationdb/contrib/replay/CMakeLists.txt

## Purpose

This CMake file integrates the Go-based `replay` TUI into the FoundationDB build. It detects Go, configures the output binary under the build tree's `bin` directory, and creates an `ALL` target that runs `go build` for the replay package.

## Important APIs, Targets, and Variables

- Requires CMake 3.13.
- `find_program(GO_EXECUTABLE go)` locates the Go toolchain.
- If Go is missing, it emits a warning and returns from the subdirectory, so the target is not available.
- `execute_process(COMMAND ${GO_EXECUTABLE} version ...)` records/logs the installed Go version but does not enforce the warned Go 1.21+ minimum.
- `REPLAY_OUTPUT_DIR` is `${CMAKE_BINARY_DIR}/bin`.
- `REPLAY_BINARY` is `${REPLAY_OUTPUT_DIR}/replay`.
- `file(GLOB REPLAY_GO_SOURCES "*.go")` tracks all Go files in the current source directory.
- `REPLAY_GO_MOD` and `REPLAY_GO_SUM` point at package module files.
- `add_custom_command(OUTPUT ${REPLAY_BINARY} COMMAND ${GO_EXECUTABLE} build -o ${REPLAY_BINARY} . WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR} DEPENDS ...)` builds the binary.
- `add_custom_target(replay ALL DEPENDS ${REPLAY_BINARY} SOURCES ${REPLAY_GO_SOURCES})` makes replay build by default when Go exists.

## Control Flow

CMake configuration first tries to find `go`. Missing Go is non-fatal for the broader build. When found, it logs the Go version, creates the binary output directory, gathers source dependencies, registers a custom command to build the Go module, and exposes an `ALL` target named `replay`.

At build time, the custom command runs `go build` from the replay source directory and emits the binary into the CMake build `bin` directory. Rebuilds are dependency-driven by the listed Go source files and module files.

## State and Persistence Behavior

The build artifact is persistent at `${CMAKE_BINARY_DIR}/bin/replay`. Go module downloads and build caches are managed by the Go toolchain outside this CMake file unless overridden by environment variables. The CMake source glob is evaluated at configure time, so adding new `.go` files may require reconfiguration depending on generator behavior.

## Dependencies and Integration Points

The file depends on a Go toolchain and the replay package's `go.mod` / `go.sum`. It plugs into the FoundationDB CMake tree as an optional contribution target. The `ALL` setting means replay becomes part of the default build only on systems where Go is present.

## Risks and Edge Cases

- The warning says Go 1.21+ is needed, but the script does not parse or enforce the version.
- `file(GLOB ...)` is not configured with `CONFIGURE_DEPENDS`, so newly added `.go` files may not trigger CMake reconfiguration.
- `go build` may download modules, which can make builds network-dependent unless dependencies are already cached or vendored.
- The binary name has no Windows executable suffix handling.
- Because the target is `ALL`, an available but misconfigured Go toolchain can fail default builds that might otherwise not need replay.

## Test Signals

Configuration tests should cover with-Go and without-Go environments. Build tests should verify `${CMAKE_BINARY_DIR}/bin/replay` appears, source changes trigger rebuilds, `go.mod`/`go.sum` changes trigger rebuilds, and invalid/old Go versions produce actionable failures if version enforcement is later added.
