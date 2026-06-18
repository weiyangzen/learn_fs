# sources/storage-engines/pebble/internal/rawalloc/rawalloc_gccgo.go

## Purpose
This build-tagged file declares the runtime allocation hook for gccgo builds, allowing `rawalloc.New` to call `runtime.mallocgc`.

## Important APIs, Types, and Functions
Under `//go:build gccgo`, it declares `//extern runtime.mallocgc` and `func mallocgc(size uintptr, typ unsafe.Pointer, needzero bool) unsafe.Pointer`.

## Control Flow and State
There is no executable control flow in this file beyond the external symbol declaration. Runtime state is delegated to gccgo's runtime.

## Dependencies and Integration
It imports `unsafe` and is selected only for gccgo builds. It supplies the same `mallocgc` symbol expected by `rawalloc.go`, preserving source compatibility with the gc implementation.

## Risks and Edge Cases
This relies on gccgo runtime internals and the exact symbol/signature. If the runtime changes, builds or allocation semantics may break. The `needzero=false` argument is passed by callers through `rawalloc.New`, so the same uninitialized-memory risks apply.

## Test Signals
No direct tests target gccgo selection here. Build coverage under gccgo would be required to validate this path.
