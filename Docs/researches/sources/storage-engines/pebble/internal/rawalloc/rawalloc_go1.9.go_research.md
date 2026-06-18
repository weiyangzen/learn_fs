# sources/storage-engines/pebble/internal/rawalloc/rawalloc_go1.9.go

## Purpose
This build-tagged file declares the runtime allocation hook for standard gc Go builds at Go 1.9 and later, allowing `rawalloc.New` to allocate unzeroed memory.

## Important APIs, Types, and Functions
Under `//go:build gc && go1.9`, it uses `//go:linkname mallocgc runtime.mallocgc` to bind a local `mallocgc(size uintptr, typ unsafe.Pointer, needzero bool) unsafe.Pointer` declaration to the private runtime function.

## Control Flow and State
There is no ordinary control flow. The file creates a link-time binding to a runtime implementation that `rawalloc.go` calls.

## Dependencies and Integration
It imports `unsafe` and uses the `go:linkname` compiler directive. It is tightly coupled to the Go runtime and selected for the usual gc toolchain.

## Risks and Edge Cases
`go:linkname` bypasses package encapsulation and is version-sensitive. The comment acknowledges that this is tied to Go release behavior. Runtime signature changes would produce build or runtime failures. It also participates in the uninitialized-memory risk of `rawalloc.New`.

## Test Signals
Only benchmark coverage appears in the listed tests. Build success under the configured Go toolchain is the primary signal that the linkname still resolves.
