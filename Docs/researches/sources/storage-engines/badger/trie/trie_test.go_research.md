# sources/storage-engines/badger/trie/trie_test.go

## Purpose
This file tests the prefix trie in `trie.go`, including normal prefixes, nil/empty prefixes, deletion and pruning, ignore-byte parsing, and wildcard prefix matching.

## Important Tests
- `TestGet` adds overlapping prefixes and confirms that root/nil IDs and shorter prefix IDs are returned for matching keys.
- `TestTrieDelete` validates ID removal, deletion of nil-prefix IDs, idempotent deletion of absent IDs, and pruning back to a single empty root.
- `TestParseIgnoreBytes` checks single indices, zero index, and comma/range syntax with spaces.
- `TestPrefixMatchWithHoles` adds exact and wildcard matches, verifies expected match sets for several keys, then deletes wildcard and exact matches and checks node pruning.

## Control Flow and State Behavior
Tests call `Trie.Add`, `AddMatch`, `Get`, `Delete`, and `DeleteMatch`, then compare returned ID maps or sorted ID slices. `numNodes` is used as a structural signal that deletion prunes empty nodes. The wildcard test constructs `pb.Match` values with `IgnoreBytes` strings and uses sorted output to avoid map-order nondeterminism.

## Dependencies and Integration Points
The tests use `testify/require`, `sort`, `testing`, and protobuf `pb.Match`. They are in package `trie`, so they can inspect unexported helpers such as `parseIgnoreBytes` and `numNodes`.

## Risks and Edge Cases
The tests do not cover invalid ignore-byte strings, reversed ranges, negative indices, or concurrent access. They also do not benchmark wildcard-heavy tries. The existing coverage is focused on intended valid syntax and deletion idempotence.

## Test Signals
The test suite confirms that root IDs match all keys, shorter prefixes match longer keys, wildcard positions consume exactly one byte, and delete operations remove IDs and compact unused branches.
