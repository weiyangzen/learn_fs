# sources/storage-engines/pebble/internal/testutils/reflect.go

## Purpose
This file provides a reflection helper to detect whether a Go type contains any pointers. It is useful in tests that verify memory layout or allocation-safety assumptions.

## Important APIs, Types, and Functions
`AnyPointers(typ reflect.Type)` returns true for pointer-containing kinds, false for scalar no-pointer kinds, and recursively examines struct fields and array elements. `kindPointers` maps `reflect.Kind` values to `kindNoPointer`, `kindHasPointer`, or `kindMaybeHasPointer`.

## Control Flow and State
The function first checks the kind lookup table. Structs recurse over all fields, arrays recurse over their element type, and unexpected maybe-kind values panic. The lookup table is package-level immutable state.

## Dependencies and Integration
It depends on `reflect` and Cockroach errors. It can support tests for cache/block layout, unsafe structures, or raw allocation assumptions.

## Risks and Edge Cases
The table must stay in sync with Go's `reflect.Kind` enumeration. If new kinds are added beyond the table length, indexing could panic. Struct recursion includes unexported fields because only types are examined. It treats strings, slices, maps, chans, funcs, interfaces, pointers, and unsafe pointers as pointer-containing.

## Test Signals
No direct tests are listed. Callers should add coverage if relying on it for critical layout gates.
