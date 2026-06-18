# sources/storage-engines/badger/watermark_edge_test.go

## Purpose
This regression test stresses Badger transaction watermarks and conflict detection under many concurrent overlapping transactions. It expects each worker to observe a conflict in a constructed interleaving.

## Important APIs, Types, And Functions
`TestWaterMarkEdgeCase` launches 1000 goroutines through `runBadgerTest`. `doWork` creates two random keys, opens two writable transactions, interleaves reads/writes, commits `tx2`, then tries to commit `tx1`. Helper functions generate random key suffixes, wrap `Txn.Get`, wrap `Txn.Set`, and add crypto-random millisecond delays.

## Control Flow
Each goroutine reads key state through both transactions, writes `tx2` to two keys, commits it, then writes and rereads `tx1` on a key that was changed by `tx2`. The top-level test expects `doWork` to return an error wrapping `ErrConflict`; any success or different error is fatal.

## State And Persistence Behavior
The test mutates real DB state but uses randomly generated keys per worker, so conflicts are local to each pair of transactions. It exercises oracle/watermark state for read timestamps and conflict windows rather than long-lived persisted files.

## Dependencies And Integration Points
It integrates transaction read sets, write sets, commit conflict checks, and Badger's watermark/oracle internals indirectly. Crypto randomness and timed delays increase scheduling diversity.

## Risks And Edge Cases
Because delays are random, the test is partly timing-sensitive, though the operation order is deterministic inside each goroutine. It panics from helpers on unexpected non-`ErrKeyNotFound` or set failures.

## Test Signals
The signal is strict: all 1000 workers must report conflicts. A success indicates a lost conflict edge or watermark/oracle ordering regression.
