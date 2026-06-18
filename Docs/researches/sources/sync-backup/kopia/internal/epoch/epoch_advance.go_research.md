# sources/sync-backup/kopia/internal/epoch/epoch_advance.go

Purpose: decides whether the current repository epoch should advance based on age, blob count, and total blob size.

Important APIs/types/functions: private `shouldAdvance`.

Control flow: returns false for no blobs, scans metadata to find min timestamp, max timestamp, and total length, rejects if elapsed time is below `minEpochDuration`, then returns true if blob count meets/exceeds the count threshold or total size meets/exceeds the size threshold.

State and persistence behavior: stateless computation over blob metadata. Epoch marker writing is handled by `Manager.MaybeAdvanceWriteEpoch`.

Dependencies/integration: used by epoch manager maintenance logic with `Parameters` thresholds.

Risks/test signals: threshold comparisons are inclusive for count and size, but time duration must be at least the minimum. Tests cover empty, insufficient age, size threshold, count threshold, and non-advancing cases.
