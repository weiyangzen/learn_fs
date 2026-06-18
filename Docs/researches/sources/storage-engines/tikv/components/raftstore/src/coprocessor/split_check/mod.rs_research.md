# sources/storage-engines/tikv/components/raftstore/src/coprocessor/split_check/mod.rs

## Purpose
`split_check/mod.rs` ties together the concrete split checkers and defines the split-check host used during raftstore split scans.

## Important APIs, Types, And Functions
The module re-exports `HalfCheckObserver`, `KeysCheckObserver`, `SizeCheckObserver`, `TableCheckObserver`, and approximate-stat helpers. `Host<'a, E>` owns a list of boxed `SplitChecker<E>`, the `SplitReason`, and a borrowed `Config`. `calc_split_keys_count` computes how many split keys are needed from region size/key count, split threshold, max per region, and batch limit.

## Control Flow
Observers add checkers through `Host::add_checker`. `policy` returns `Approximate` if any checker requests approximate mode; otherwise it returns `Scan`. `on_kv` feeds each scanned `KeyEntry` to each checker and aborts if any checker asks to stop. `split_keys` and `approximate_split_keys` return the first non-empty result from checkers in registration order. `approximate_bucket_keys` uses approximate size to decide whether buckets should be generated, then uses a size checker to produce bucket boundaries.

`calc_split_keys_count` returns zero below `max_count_per_region`; above that it chooses the larger of rounded split-threshold division minus one and max-count division, capped by `batch_split_limit`.

## State And Persistence Behavior
`Host` only stores in-memory checkers for one split-check task. It does not persist, but its results drive later `AskSplit` or `RefreshRegionBuckets` scheduling in raftstore.

## Dependencies And Integration Points
Depends on `kvproto` split policies/reasons, shared `Config`, `Bucket`, `KeyEntry`, and coprocessor `SplitChecker` traits. It is constructed by `CoprocessorHost::new_split_checker_host` after registered split observers inspect a region.

## Risks
Only the first checker with non-empty split keys wins, so observer priority and checker order determine split behavior when several policies could split. `policy` escalates to approximate if any checker wants it, which can affect bucket-only checks. `calc_split_keys_count` uses floating-point rounding; tests protect expected ranges, but boundary behavior should be treated carefully.

## Test Signals
Tests live in child modules. They cover checker selection, split-key count math, scan versus approximate policies, bucket generation, table-boundary splitting, and range-property helper behavior.
