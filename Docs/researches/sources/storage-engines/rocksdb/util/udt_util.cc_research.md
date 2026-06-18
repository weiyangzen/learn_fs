# sources/storage-engines/rocksdb/util/udt_util.cc

## Purpose

Implements utilities for user-defined timestamp (UDT) recovery from WAL write batches, option-change validation, cutoff timestamp conversion, and adding timestamps to range bounds.

## APIs, control flow, and state

Internal recovery classification maps running and recorded timestamp sizes to noop, strip, pad, or unrecoverable. `HandleWriteBatchTimestampSizeDifference` first checks all running CFs for quick consistency, then collects CF ids from the batch, validates according to verify/reconcile mode, and when needed rebuilds a new `WriteBatch` using `TimestampRecoveryHandler` while preserving sequence number. The handler rewrites every supported write operation by stripping old timestamps, appending min timestamps, or copying dropped-CF entries unchanged; transaction markers are copied through with policy restrictions. `ValidateUserDefinedTimestampsOptions` compares comparator names and `.u64ts` suffix transitions against persist flags. Range helper appends max/min timestamps depending on inclusive/exclusive semantics.

## Dependencies and integration

It depends on DB format helpers, write batch internals, wide-column serialization, fixed-width coding, and `CollectColumnFamilyIdsFromWriteBatch`. This code runs during WAL recovery and column-family open validation.

## Risks and test signals

Risks are data-loss-sensitive: wrong padding/stripping changes user keys during recovery. Nonzero mismatched timestamp sizes are intentionally unrecoverable. Tests cover consistent, dropped, strip, pad, unrecoverable cases across many write batch record types; option validation for enabling/disabling UDT; and full-history timestamp conversion.
