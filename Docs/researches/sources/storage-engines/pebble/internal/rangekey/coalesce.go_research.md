# sources/storage-engines/pebble/internal/rangekey/coalesce.go

## Purpose
This file resolves Pebble range-key semantics for a single fragmented span with common bounds. It removes range keys shadowed by newer sets, unsets, and deletes, optionally under a snapshot visibility cutoff, and supplies a specialized transformer for shared ingested sstables.

## Important APIs, Types, and Functions
`Coalesce(suffixCmp, keys, dst)` is the public wrapper that coalesces with all sequence numbers visible and sorts the result by internal trailer. `CoalesceInto(suffixCmp, dst, snapshot, keys)` performs the core work and returns keys sorted by suffix, with a trailing range-key delete appended if one is visible. `ForeignSSTTransformer` implements `keyspan.Transformer`, coalesces shared foreign sstable range keys, rewrites each key to a configured sequence number, and returns trailer-descending order.

## Control Flow and State
`CoalesceInto` first scans the trailer-descending input keys, skipping keys not visible at `snapshot` and stopping at the first visible `RANGEKEYDEL`, because it shadows lower sequence numbers. It appends visible set/unset keys before the delete into `dst`, stable-sorts them by suffix, and removes duplicate suffixes by keeping the first entry, which corresponds to the newest trailer due to the original ordering. If a delete was seen, it is appended after suffix coalescing. There is no persistent state; callers own buffers and key byte lifetimes. `ForeignSSTTransformer` reuses `sortBuf` to reduce allocations.

## Dependencies and Integration
The file depends on `base`, `invariants`, `keyspan`, `slices`, `math`, and Cockroach errors. It is central to range-key compactions, range-key user iteration, and ingestion of shared sstables. `rangekeystack.UserIteratorConfig.Transform` directly uses `CoalesceInto`.

## Risks and Edge Cases
The input must be sorted by trailer descending; invariant builds panic on disorder, production builds trust the caller. Comments describe sequence-number promotion, but a TODO notes the current implementation does not actually perform that promotion in `Coalesce`. Equal sequence numbers depend on Pebble's internal key-kind ordering: sets and unsets at the same sequence number do not shadow a delete at that same sequence number. The returned order differs between APIs, so callers must respect whether they receive suffix order or trailer order.

## Test Signals
`coalesce_test.go` is datadriven and compares parsed spans against `Coalesce` string output. It provides golden coverage for shadowing semantics but does not directly test `ForeignSSTTransformer` in this file.
