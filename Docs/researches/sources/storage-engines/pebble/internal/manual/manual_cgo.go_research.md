<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/manual/manual_cgo.go -->
# sources/storage-engines/pebble/internal/manual/manual_cgo.go

Purpose: cgo-backed implementation of manual allocation using `C.calloc` and `C.free`, with a race-enabled alternate mode that sometimes uses Go allocations so the race detector can observe accesses.

Important APIs/functions: `New(purpose, n)` returns a `Buf` of size `n`; `Free(purpose, b)` releases it. The file linknames `runtime.throw` as `throw` to terminate on out-of-memory in the same style as the Go runtime. `useGoAllocation` is selected randomly in race builds.

Control flow and state: zero-size allocations return an empty `Buf` without accounting. Non-zero allocations call `recordAlloc`. Race/go-allocation mode returns a pointer into a Go byte slice; normal mode calls `calloc` so memory is zeroed before Go sees it. `Free` mangles bytes in invariant builds, records the free, and calls `C.free` only for cgo allocations.

Dependencies and integration: depends on cgo, `math/rand/v2`, `unsafe`, and `invariants`. It is the production path where cgo is available and supports block cache and memtable manual memory. Risks include strict requirement to free exactly the original `Buf`, memory leaks on missed free, dangling pointers after free, and cgo pointer rules if Go pointers are stored in C memory. The race-mode all-or-none policy mitigates mixed Go/C pointer storage in manually allocated structs.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/manual/manual_cgo.go -->
