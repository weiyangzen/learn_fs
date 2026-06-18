# sources/storage-engines/foundationdb/fdbkubernetesmonitor/CMakeLists.txt

## Purpose
This CMake file integrates the Go-based `fdb-kubernetes-monitor` binary and its Go tests into the FoundationDB build.

## Important APIs, Types, And Functions
It locates `go` and `gofmt`, collects Go sources, declares `${CMAKE_BINARY_DIR}/bin/fdb-kubernetes-monitor`, adds a custom command running `go build -o ... .`, creates an `ALL` custom target, and registers `go test -race ./...` plus a gofmt diff test.

## Control Flow
If Go is missing or the platform is Windows, it returns early. Otherwise CMake tracks `.go`, `go.mod`, and `go.sum` as dependencies, builds from the module directory, and adds CTest entries for race-enabled tests and formatting.

## State And Persistence Behavior
The build persists the monitor binary in the build `bin` directory. Tests may create Go test artifacts but no runtime state is encoded here.

## Dependencies And Integration Points
It depends on a local Go toolchain and module files. It integrates a Go subproject into the broader CMake/CTest workflow.

## Risks And Edge Cases
`file(GLOB_RECURSE ...)` can require CMake regeneration to detect new files depending on generator behavior. Race tests are slower and may require cgo/toolchain support. Windows builds silently skip the target.

## Test Signals
Build signals are a present `bin/fdb-kubernetes-monitor`, successful `fdb-kubernetes-monitor-go-tests`, and empty `gofmt -d` output.
