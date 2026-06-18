# sources/storage-engines/pebble/internal/compression/msan_on.go

## Purpose
This build-tagged file implements the MemorySanitizer hook used after codec writes.

## Important APIs, Types, And Functions
`msanWrite(p []byte)` calls `runtime.MSanWrite` with the slice's first byte pointer and length when the slice is non-empty. It is compiled under `//go:build msan`.

## Control Flow
Codec implementations call this after producing compressed or decompressed bytes so MSan knows the memory has been initialized, including when assembly or C code performed writes outside Go's ordinary instrumentation.

## State And Persistence Behavior
It updates sanitizer metadata only. There is no Pebble state or persistence.

## Dependencies And Integration Points
It imports `runtime` and `unsafe`, and pairs with `msan_off.go`. Snappy, MinLZ, and Zstd adapters call the shared hook.

## Risks And Edge Cases
The function must avoid taking `&p[0]` for empty slices, which it does. Incorrect length or pointer would produce sanitizer inaccuracies.

## Test Signals
Validation is primarily MSan build/test execution. Non-MSan tests do not compile this file.
