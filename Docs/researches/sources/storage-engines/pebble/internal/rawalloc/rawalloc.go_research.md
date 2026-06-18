# sources/storage-engines/pebble/internal/rawalloc/rawalloc.go

## Purpose
This file exposes `rawalloc.New`, a low-level byte slice allocator that returns uninitialized memory. It exists to avoid the zeroing cost of `make([]byte, len, cap)` where callers will overwrite the buffer before reading it.

## Important APIs, Types, and Functions
`New(len, cap int) []byte` calls runtime `mallocgc(uintptr(cap), nil, false)` and converts the returned pointer into a byte slice of capacity `cap` and length `len` using `unsafe.Slice`.

## Control Flow and State
Allocation is a single runtime call. There is no package state or persistence. The returned memory is managed by the Go runtime but is explicitly not zero-initialized.

## Dependencies and Integration
The file depends on `unsafe` and a platform/build-specific `mallocgc` declaration supplied by sibling files. It is an internal performance primitive and should only be used by callers that can guarantee full initialization before reads.

## Risks and Edge Cases
This is inherently unsafe. Reading unwritten bytes can expose stale heap contents and cause nondeterministic behavior. The function does not validate `len <= cap`; slicing `[:len]` will panic if violated. It relies on Go runtime internals whose signatures and linkability can change.

## Test Signals
`rawalloc_test.go` contains only benchmarks comparing this allocator with `make`, not correctness tests. The absence of functional tests reflects that correctness relies on careful caller discipline.
