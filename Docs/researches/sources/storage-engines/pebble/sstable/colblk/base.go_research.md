## sources/storage-engines/pebble/sstable/colblk/base.go

Purpose: Provides low-level alignment constants/helpers and runtime memory function linknames used by columnar block encoding/decoding code.

Important APIs/types/functions: `align`, `alignWithZeroes`, constants `align16`, `align32`, `align64`, shift constants, and linknamed `memmove`/`mallocgc`.

Control flow: `align` rounds an integer offset up to the next multiple of a power-of-two alignment value. `alignWithZeroes` computes the aligned offset and writes zero bytes into padding for deterministic encodings when buffers are reused.

State and persistence behavior: Alignment affects columnar block binary layouts and deterministic padding bytes. The runtime linknames have no persisted state but are low-level allocation/copy hooks for other colblk code.

Dependencies and integration points: Used by bitmap and other columnar encoders/decoders. Depends on `unsafe`, `golang.org/x/exp/constraints`, and Go runtime internals through `go:linkname`.

Risks: `align` assumes power-of-two `val`. Runtime linknames are explicitly risky; comments note future Go versions may remove access and suggest maintained assembly alternatives. Misaligned or nondeterministic padding would affect encoded block bytes and tests.

Test signals: No direct tests here. `bitmap_test.go` indirectly exercises `align` and `alignWithZeroes` through bitmap offset/padding cases.
