# sources/user-network-fs/rclone/fs/hash/hash_test.go

## Purpose
`hash_test.go` validates the hash registry, set bitmask helpers, multihash streaming, known digest outputs, flag parsing, and initial type-value stability.

## Important APIs, types, and functions
The suite exercises `hash.Set` methods, `hash.NewHashSet`, `Supported`, `NewMultiHasher`, `NewMultiHasherTypes`, `Stream`, `StreamTypes`, `Type.String`, `Type.Set`, and the `pflag.Value` interface implementation. `hashTestSet` contains canonical digest vectors for non-empty and empty byte slices.

## Control flow
Tests build sets, add/overlap/subset them, check enumeration and first-choice behavior, stream fixed buffers through `MultiHasher` or `Stream*`, and compare every returned digest to expected hex strings. Setter tests verify accepted names and aliases and rejected near-misses.

## State and persistence behavior
The tests use the package global registry but do not mutate it. No persistent state is written.

## Dependencies and integration points
The tests import rclone `fs` only for logging, `pflag` for interface checking, and testify for assertions. They protect behavior consumed by backend `Hashes()` declarations, copy/check logic, and command-line hash selection.

## Risks and edge cases
Digest vectors catch algorithm swaps, wrong xxh128 length/endian behavior, and accidental registration changes. The type stability test only asserts early values, so adding later hash types remains possible but reordering initial registrations should fail.

## Test signals
Coverage is strong for normal hash paths: empty input, multiple algorithms in one pass, single requested hash, set string formatting, parser aliases such as `SHA-1`, and rejection of unsupported spelling like `Sha-1`.

Source-read signal: reviewed complete local file (219 lines). Types observed: `hashTest`. Functions/methods observed: `TestHashSet`, `TestMultiHasher`, `TestMultiHasherTypes`, `TestHashStream`, `TestHashStreamTypes`, `TestHashSetStringer`, `TestHashStringer`, `TestHashSetter`, `TestHashTypeStability`.
