# sources/object-store/rustfs/crates/common/src/last_minute.rs

## Purpose
`last_minute.rs` implements rolling last-minute accumulation primitives for latency/size statistics. It provides per-second ring-buffer accumulation (`LastMinuteLatency`) and size-bucketed histograms (`LastMinuteHistogram`).

## Important APIs, Types, and Functions
`AccElem` stores `total`, `size`, and count `n`, with `add`, `merge`, and `avg`. `LastMinuteLatency` stores 60 `AccElem` slots plus `last_sec`, with `merge`, `add`, `add_all`, `get_total`, and `forward_to`. `LastMinuteHistogram` stores a vector of `LastMinuteLatency` buckets and exposes `merge`, `add`, and `get_avg_data`. `size_to_tag` maps sizes to six categories. Private/dead-code types `TimedAction` and `SizeCategory` appear to be earlier or future helpers.

## Control Flow
`LastMinuteLatency::forward_to` advances the ring to a target timestamp: no-op for same/past time, clears all slots for gaps of 60 seconds or more, and otherwise clears each newly entered slot one second at a time. `add` uses current UNIX seconds, forwards, and adds a duration to the current slot. `add_all` does the same for an explicit timestamp and `AccElem`. `get_total` forwards to current time and merges all slots. `merge` aligns two windows to the later `last_sec`, then sums corresponding slots into a new `LastMinuteLatency`. Histogram `add` chooses a size bucket and records duration in that bucket.

## State and Persistence Behavior
State is in-memory and mutable. `AccElem::add` stores duration seconds only (`as_secs`), truncating subsecond data. `AccElem::merge` uses wrapping arithmetic for all fields, while `LastMinuteLatency::merge` sums fields with normal `+`, which can panic in debug on overflow. No synchronization is built in.

## Dependencies and Integration Points
Used by `bucket_stats::ReplicationLatency` for upload latency summaries. It depends only on `std::time`. The tests form a detailed behavior contract for rolling windows.

## Risks and Edge Cases
`LastMinuteHistogram` derives `Default`, leaving `histogram` empty; calling `add` on a default value indexes into an empty vector and will panic unless constructed elsewhere with buckets. `SIZE_LAST_ELEM_MARKER` is 10 while `size_to_tag` returns only 0-5, creating unused buckets if initialized to length 10. `LastMinuteHistogram::merge` ignores the returned merged latency from `LastMinuteLatency::merge`, so it may not actually update buckets as intended. Subsecond durations are truncated to zero in `AccElem`. Time moving backward is ignored by `forward_to`.

## Test Signals
Extensive tests cover `AccElem` defaults, add/merge/avg, subsecond truncation, wrapping overflow in `AccElem::merge`, ring forwarding for same/past/small/large gaps, explicit timestamp addition, same/different-time merges, wraparound, realistic 60-second windows, clone/debug behavior, boundary clearing at exactly 60 seconds, `get_total` with current timestamps, index calculation, concurrent-pattern simulation, and large values.
