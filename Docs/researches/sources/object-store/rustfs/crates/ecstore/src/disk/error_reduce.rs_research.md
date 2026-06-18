# sources/object-store/rustfs/crates/ecstore/src/disk/error_reduce.rs

## Purpose
`error_reduce.rs` reduces per-disk operation results into quorum-level success or failure. It encodes which disk errors should be ignored for object, bucket, and base operations, picks dominant non-ignored errors, returns read/write quorum errors when not enough matching success/error votes exist, and builds write-quorum failure summaries for logging and metrics.

## Important APIs, Types, And Functions
- `WriteQuorumFailureSummary` captures required quorum, achieved successes, failed count, total disks, offline disk count, ignored failures, retryable internode failures, dominant error, and a stable label for the dominant error.
- `OBJECT_OP_IGNORED_ERRS`, `BUCKET_OP_IGNORED_ERRS`, and `BASE_IGNORED_ERRS` define context-specific errors excluded from dominant-error voting.
- `reduce_write_quorum_errs` and `reduce_read_quorum_errs` call `reduce_quorum_errs` with `ErasureWriteQuorum` or `ErasureReadQuorum`.
- `reduce_quorum_errs` returns the dominant error if it reaches quorum; otherwise it returns the supplied quorum error.
- `reduce_errs` counts `None` as successful nil results, ignores configured errors, counts cloned `DiskError` values, and prefers nil on ties.
- `build_write_quorum_failure_summary` computes richer diagnostics around a failed or marginal write.
- `is_ignored_err`, `count_errs`, `count_retryable_failures`, and `is_all_buckets_not_found` are small helpers used by set, bucket, and healing code.

## Control Flow
The reduction model treats the input slice as one result per disk. `None` means success. `Some(error)` means that disk failed with a specific error. `reduce_errs` first counts successes, then builds a frequency map of non-ignored errors. It picks the most frequent non-ignored error, then compares it with the success count. If success count is greater, or tied and nonzero, the reduced result is success (`None`). Otherwise the dominant error wins.

`reduce_quorum_errs` then compares the winning count with the required quorum. If the winning count reaches quorum, it returns the winning error, which can be `None` for quorum success. If not, the operation fails with a generic read/write quorum error. This means ignored errors can reduce the available vote pool without becoming the dominant returned error.

`build_write_quorum_failure_summary` recomputes success/failure counts and uses `dominant_error_label` to produce labels such as `nil_dominated`, `disk_not_found`, `short_write`, an internode HTTP metric label, or `other_error`.

## State And Persistence Behavior
This file is stateless. Its decisions directly affect persisted object/write behavior because quorum reduction decides whether multi-disk writes, deletes, reads, metadata updates, bucket operations, multipart operations, and erasure encoding are accepted or rolled back/reported as failed.

## Dependencies And Integration Points
The module depends on `DiskError` and its internode HTTP helpers. `set_disk.rs`, `set_disk/read.rs`, `set_disk/write.rs`, `set_disk/metadata.rs`, and `set_disk/multipart.rs` call read/write reducers for object operations. `erasure_coding/encode.rs` uses `build_write_quorum_failure_summary` to log write-quorum diagnostics and retryable internode failures. `rpc/peer_s3_client.rs` uses bucket ignored errors and `is_all_buckets_not_found` for bucket healing, make/list/delete flows. `store_init.rs` uses count/reduce helpers while initializing disks.

## Risks And Edge Cases
- The parameter is named `quorun` in several functions; it is harmless but can obscure intent.
- `HashMap::into_iter().max_by` does not define deterministic tie-breaking among different non-nil errors with equal counts. Nil ties are deterministic, but non-nil ties may produce whichever the map iteration yields.
- Ignored errors are excluded from dominant voting but still counted as failed in summaries, so callers must choose ignored sets carefully.
- `DiskError::Hash` collapses all I/O errors to one numeric code, while equality distinguishes kind/message. Frequency counting for many distinct I/O errors may have high collision cost.
- `is_all_buckets_not_found` returns false if any disk succeeded (`None`), so it only means every reported result is a not-found style error.

## Test Signals
Tests cover basic dominant-error reduction, ignored errors, quorum success versus generic quorum failure, counting errors, ignored-error matching, write-quorum summary fields, preservation of internode retry labels such as `connection_reset`, and nil tie-breaking.
