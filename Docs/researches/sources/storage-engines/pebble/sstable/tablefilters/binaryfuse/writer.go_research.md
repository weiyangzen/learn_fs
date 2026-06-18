# sources/storage-engines/pebble/sstable/tablefilters/binaryfuse/writer.go

## Purpose
Implements `base.TableFilterWriter` for binary fuse filters, translating SSTable keys into xxh3 hashes and final filter bytes.

## Important APIs, Types, And Functions
`tableFilterWriter` stores `bitsPerFingerprint` and a `hashCollector`. `newTableFilterWriter`, `init`, `AddKey`, and `Finish` implement construction and the table-filter writer interface.

## Control Flow
The policy creates a writer with a configured fingerprint width. SSTable writing calls `AddKey` for each filter key, storing the xxh3 hash. `Finish` calls `buildFilter`; on success it resets the collector and returns filter bytes plus `Family`, otherwise it returns `ok=false`.

## State And Persistence Behavior
The collector is transient until `Finish`. The returned filter data is persisted in the SSTable filter block. `Finish` releases pooled hash blocks through `Reset` only on successful build.

## Dependencies And Integration Points
Depends on Pebble `base` filter interfaces, `xxh3`, `hashCollector`, and `buildFilter`. Created from `filterPolicyImpl.NewWriter`.

## Risks And Edge Cases
Empty filters, too-large filters, or construction failure produce no filter. If a caller abandons a writer without `Finish`, hash blocks are not reset through this file's path.

## Test Signals
Covered by binary fuse end-to-end tests, build tests, and writer benchmarks.
