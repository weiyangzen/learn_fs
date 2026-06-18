# sources/storage-engines/pebble/internal/compression/msan_off.go

## Purpose
This build-tagged file provides the no-op MemorySanitizer hook for non-MSan builds.

## Important APIs, Types, And Functions
`func msanWrite(p []byte) {}` is compiled under `//go:build !msan`.

## Control Flow
Compression/decompression implementations call `msanWrite` after assembly or external codec writes. In non-MSan builds, calls do nothing.

## State And Persistence Behavior
No state is mutated and no persistence exists.

## Dependencies And Integration Points
It pairs with `msan_on.go` and is called from Snappy, MinLZ, and Zstd implementations.

## Risks And Edge Cases
The only risk is build selection: if an MSan build accidentally uses this file, sanitizer may report false positives or miss initialization.

## Test Signals
Compile-time build tags are the validation. Ordinary compression tests run through this no-op in non-MSan builds.
