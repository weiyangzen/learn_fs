# sources/storage-engines/pebble/sstable/tablefilters/binaryfuse/binary_fuse.go

## Purpose
Defines Pebble's binary fuse table filter policy family and decoder registration. It exposes configurable fingerprint widths as `base.TableFilterPolicy` values for SSTable writers and a `base.TableFilterDecoder` for readers.

## Important APIs, Types, And Functions
`Family` is the table filter family string. `SupportedBitsPerFingerprint` mirrors bitpacking support. `FilterPolicy(bitsPerFingerprint)` validates 4, 8, 10, 12, or 16 bits and returns `filterPolicyImpl`. `filterPolicyImpl.Name` emits `binaryfuse(N)`, `NewWriter` creates a writer, and `PolicyFromName` parses policy names. `Decoder` implements `Family` and `MayContain`.

## Control Flow
Callers choose a policy during SSTable writing. The policy creates a writer that hashes keys and emits binary fuse filter bytes tagged with `Family`. During reads, the table-filter dispatcher selects `Decoder` by family and calls `MayContain`, which hashes the lookup key with xxh3 and delegates to `mayContain`.

## State And Persistence Behavior
The only persistent output is policy name metadata and filter bytes stored in SSTables. The file itself has no mutable state beyond immutable policy structs.

## Dependencies And Integration Points
Integrates with `base.TableFilterPolicy`, `base.TableFilterWriter`, `base.TableFilterDecoder`, `tablefilters.PolicyFromName`, `bitpacking`, `xxh3`, and the binary fuse build/probe code in neighboring files.

## Risks And Edge Cases
Unsupported fingerprint widths panic at policy construction and are ignored by name parsing. Older Pebble binaries may not understand this family, making format compatibility a deployment concern. FPR and bits/key are documented as size-dependent, especially for smaller filters.

## Test Signals
Covered by binary fuse end-to-end tests, policy name parsing paths, build tests, and writer/probe benchmarks in this package.
