# sources/user-network-fs/rclone/fs/hash/hash.go

## Purpose
`hash.go` defines rclone's hash type registry, hash-set bitmask operations, streaming hash calculators, and multihash writer. It standardizes MD5, SHA-1, Whirlpool, CRC-32, SHA-256, SHA-512, BLAKE3, XXH3-64, and XXH3-128 support for filesystem backends and operations.

## Important APIs, types, and functions
Important exports are `Type`, `Set`, `RegisterHash`, `SupportOnly`, `ErrUnsupported`, hash constants, `Supported`, `Width`, `Stream`, `StreamTypes`, `MultiHasher`, `NewMultiHasher`, `NewMultiHasherTypes`, `Equals`, and `HelpString`. `Type.Set` implements flag parsing by lowercase name or exact alias. `xxh128Hasher` adapts `xxh3.Hasher` to a 128-bit `hash.Hash`.

## Control flow
`init` registers algorithms in stable bit order. `StreamTypes` builds requested hashers, copies input through a multiwriter, and returns hex sums. `MultiHasher.Write` updates all hashers while counting bytes; `Sums`, `Sum`, and `SumString` return accumulated hashes. `fromTypes` rejects sets not contained in `Supported()`. `Set` methods perform bitwise add/overlap/subset, enumeration, first-bit selection, and population count.

## State and persistence behavior
Global registry maps and the `supported` slice are process state initialized at package load. `SupportOnly` mutates supported hashes for tests and returns the old slice. Hash calculations are in-memory and do not persist data.

## Dependencies and integration points
Backends expose supported sets through `Fs.Hashes()`, sync/check operations compare hashes with `Equals`, local/object helpers use `MultiHasher`, and CLI help/flags use `Type.Set`, `Type.String`, and `HelpString`. External hash implementations are Whirlpool, BLAKE3, and xxh3.

## Risks and edge cases
Hash `Type` values are bit positions, so registration order is compatibility-sensitive. `Type.String` panics on unknown types. `fromTypes` rejects unknown bitmasks based on current `Supported`, which tests can mutate. `Equals` treats empty hashes as matching, which is intentional for unknown hashes but dangerous if callers assume strict equality.

## Test signals
`hash_test.go` validates set operations, known digest vectors for all registered algorithms including empty input, stream and multihasher behavior, string/flag parsing, and type stability for `None`, `MD5`, and `SHA1`.

Source-read signal: reviewed complete local file (421 lines). Types observed: `Type`, `hashDefinition`, `xxh128Hasher`, `MultiHasher`, `Set`. Functions/methods observed: `RegisterHash`, `SupportOnly`, `Sum`, `Size`, `init`, `Supported`, `Width`, `Stream`, `StreamTypes`, `String`, `Set`, `Type`, `fromTypes`, `toMultiWriter`, `NewMultiHasher`, `NewMultiHasherTypes`.
