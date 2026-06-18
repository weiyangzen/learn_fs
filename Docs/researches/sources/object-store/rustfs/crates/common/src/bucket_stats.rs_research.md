# sources/object-store/rustfs/crates/common/src/bucket_stats.rs

## Purpose
`bucket_stats.rs` defines `ReplicationLatency`, a helper for tracking recent replication upload latency by object size category.

## Important APIs, Types, and Functions
`ReplicationLatency` owns a `last_minute::LastMinuteHistogram` named `upload_histogram`. `merge` merges another latency histogram into this one. `get_upload_latency` returns a `HashMap<String, u64>` from size bucket label to average latency in milliseconds. `update` records a size/duration sample. `size_tag_to_string` maps histogram indexes to human-readable size buckets from `<1 KiB` through `>1 GiB`.

## Control Flow
Updates go to the underlying histogram using `size` to choose a bucket. Reads call `get_avg_data`, iterate every returned `AccElem`, compute `avg()`, convert to milliseconds, and label each bucket. Merges delegate to `LastMinuteHistogram::merge`.

## State and Persistence Behavior
State is in-memory rolling histogram data. No persistence or synchronization is provided in this type; callers must handle sharing/mutability.

## Dependencies and Integration Points
Depends on `crate::last_minute`. It likely feeds bucket or replication metrics APIs elsewhere in RustFS. The returned `HashMap` is suitable for JSON/metrics reporting.

## Risks and Edge Cases
`ReplicationLatency` has no `Default` implementation in this file despite owning a private histogram, so construction may happen elsewhere or be incomplete. `get_upload_latency` returns labels for every histogram element; `LastMinuteHistogram` currently returns ten elements while `size_tag_to_string` only defines six explicit labels and maps the rest to `Size > 1 GiB`, causing duplicate labels to overwrite in the `HashMap`. Duration precision depends on `LastMinuteHistogram`/`AccElem`, which stores seconds, so millisecond output may be coarse or zero for subsecond durations.

## Test Signals
No tests live in this file. Behavior is indirectly constrained by extensive `last_minute.rs` tests for bucket windowing, averages, wraparound, and overflow.
