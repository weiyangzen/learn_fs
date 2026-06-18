# sources/storage-engines/badger/trie/trie.go

## Purpose
This file implements a prefix trie with optional wildcard byte positions, used to map Badger match prefixes to table or stream IDs. It supports adding, deleting, and querying IDs associated with prefixes, including "holes" specified by index ranges.

## Important APIs, Types, and Functions
- `node` stores byte children, a wildcard `ignore` child, and IDs that match at that prefix.
- `Trie` owns a root node and is constructed by `NewTrie`.
- `parseIgnoreBytes` parses comma-separated indices and ranges like `"3, 5-8"`.
- `Add`, `AddMatch`, `Delete`, and `DeleteMatch` mutate the trie.
- Internal `fix` performs add/delete traversal for both exact and ignore-byte paths.
- `Get` and recursive `get` collect all IDs matching prefixes along a key path.
- `removeEmpty` prunes empty nodes after deletion; `numNodes` is a test helper.

## Control Flow and State Behavior
`AddMatch` parses ignore bytes into a boolean slice extended to the prefix length. For each prefix byte, exact positions traverse or create `children[byte]`, while ignored positions traverse or create the `ignore` branch. IDs are stored only at the terminal node for the prefix. Nil and empty prefixes attach IDs to the root, making them match every key.

`Get` starts at root, adds IDs at each visited node, recurses into the wildcard child if present with one byte consumed, and recurses into the exact child for the current byte. Results are deduplicated in a `map[uint64]struct{}`. Deletion removes matching IDs from the terminal node and then prunes empty branches without removing the root.

## Dependencies and Integration Points
The trie uses `pb.Match` for prefix and `IgnoreBytes` inputs, and `y.Check`/`AssertTrue` for simple error/assert handling. It likely supports match-based routing for stream/table selection where ranges can ignore timestamp or variable bytes.

## Risks and Edge Cases
The trie is not synchronized; callers must protect concurrent mutation/query if needed. `parseIgnoreBytes` does not reject reversed ranges explicitly, resulting in no range marks when start is greater than end. Invalid integer text propagates as errors. Wildcard recursion can branch exponentially with many ignore nodes, though expected match sets are likely small.

## Test Signals
`trie_test.go` validates basic prefix matching, nil/empty prefix behavior, deletion and pruning, ignore-byte parsing, wildcard matching with ranges, and deletion of wildcard matches.
