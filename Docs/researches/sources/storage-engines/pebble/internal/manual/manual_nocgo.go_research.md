<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/manual/manual_nocgo.go -->
# sources/storage-engines/pebble/internal/manual/manual_nocgo.go

Purpose: fallback manual allocator used when cgo is unavailable, such as cross-compilation. It emulates manual allocation with per-size-class `sync.Pool`s of Go-allocated byte slices.

Important APIs/functions: `New`, `Free`, package-level `pools`, `init`, and `sizeClass`. `New` records allocation bytes and returns a pooled pointer whose backing capacity is the next power-of-two size class. `Free` mangles, clears, records free bytes, and returns the pointer to the appropriate pool.

Control flow and state: `init` installs a `New` function on every pool, allocating a byte slice of size `1 << i` and boxing its data pointer. `sizeClass` computes `bits.Len(uint(size-1))` and panics on zero in invariant builds. `Free` ignores nil data after attempting to mangle the slice, matching the empty `Buf` path.

Dependencies and integration: uses `math/bits`, `sync`, `unsafe`, errors, and invariants. It integrates behind the same `manual.New/Free` API as the cgo implementation. Risks include larger retained memory due to power-of-two classes, GC-managed lifetime despite manual API semantics, stale data exposure if clearing were skipped, and caller misuse of exact-size/purpose pairing. There are no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/manual/manual_nocgo.go -->
