# sources/sync-backup/kopia/repo/blob/throttling/throttling_storage_test.go

Purpose: verifies that the throttling storage wrapper calls throttler hooks in the expected order with the expected byte counts.

Important APIs/types/functions: `mockThrottler` records activity for every `Throttler` method. `TestThrottling` wraps map storage with a logging wrapper inside the throttling wrapper.

Control flow: the test attempts a missing full read, uploads a small blob, uploads a 30 MB blob, reads small and large blobs with unknown length, reads a partial range, gets metadata, deletes, and lists. For each operation it compares the recorded sequence against an exact expected trace.

State and persistence behavior: map storage holds two blobs; the mock holds an activity slice reset between operations.

Dependencies/integration: depends on blobtesting map storage, blob logging wrapper, gather buffers, and the throttling wrapper.

Risks and edge cases: exact sequence assertions are intentionally strict and may require updates if logging wrapper behavior changes. The test does not cover `ExtendBlobRetention`.

Test signals: failures indicate wrapper ordering changes, missing `AfterOperation`, incorrect unknown-download estimate/refund math, or incorrect upload/download byte acquisition.
