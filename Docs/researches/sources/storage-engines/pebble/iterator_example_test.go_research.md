# sources/storage-engines/pebble/iterator_example_test.go

## Purpose
Provides Go documentation examples for common Pebble iterator use. These examples are executable tests that show users how to scan all keys, scan a prefix-like key range through bounds, and seek to the first key greater than or equal to a target.

## Important APIs, Types, And Functions
`ExampleIterator` opens an in-memory Pebble DB, writes three keys, creates `db.NewIter(nil)`, and scans with `First`, `Valid`, `Next`, and `Key`. `ExampleIterator_prefixIteration` demonstrates constructing `IterOptions` with `LowerBound` and `UpperBound`, including a local `keyUpperBound` helper that computes the smallest exclusive upper bound after a byte prefix. `ExampleIterator_SeekGE` demonstrates repeated `SeekGE` calls on a single iterator.

The examples use `pebble.Open`, `pebble.Options`, `vfs.NewMem`, `DB.Set`, `DB.NewIter`, `Iterator.Close`, `DB.Close`, and `pebble.Sync`. They live in package `pebble_test`, so they exercise the public API rather than unexported internals.

## Control Flow
Each example opens an isolated in-memory DB, writes `"hello"`, `"world"`, and `"hello world"`, creates an iterator, performs the targeted scan or seeks, prints keys, closes the iterator, and closes the DB. The expected `// Output:` block checks lexicographic ordering and makes the examples part of normal `go test` validation.

Prefix-style scanning is implemented with normal iterator bounds rather than `SeekPrefixGE`: the helper returns an upper bound by incrementing the last non-`0xff` byte and truncating after it, or nil when no finite upper bound exists. The scan then uses `First`/`Next` over `[prefix, upper)`.

## State And Persistence Behavior
All state is local and in-memory. The examples write transient keys into `vfs.NewMem()` and close all resources. Values are nil because the examples are about key iteration order, not value retrieval.

The key slices printed by `iter.Key()` are consumed immediately before the next iterator movement. No long-lived references to iterator-owned memory are retained.

## Dependencies And Integration Points
These examples integrate public documentation with the test suite. Because they are in `pebble_test`, they verify that external users can import `github.com/cockroachdb/pebble` and `github.com/cockroachdb/pebble/vfs` and perform the documented workflows without internal access.

## Risks And Edge Cases
The examples intentionally avoid errors from `NewIter` by ignoring the returned error, which is acceptable for concise documentation but less complete than production code. The prefix upper-bound helper handles carry and all-`0xff` prefixes, but it demonstrates bytewise-prefix bounds rather than comparer-defined `SeekPrefixGE` prefix iteration.

Resource cleanup is explicit. If future iterator APIs change close/error expectations, these examples are useful smoke tests for public documentation drift.

## Test Signals
`go test` validates the printed ordering exactly: full scan yields `hello`, `hello world`, `world`; bounded prefix scan yields only `hello` and `hello world`; `SeekGE("a")`, `SeekGE("hello w")`, and `SeekGE("w")` land on the expected keys.
