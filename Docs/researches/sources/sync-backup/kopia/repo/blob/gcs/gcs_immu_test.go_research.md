# sources/sync-backup/kopia/repo/blob/gcs/gcs_immu_test.go

Purpose: live integration test for Google Cloud Storage object retention/immutability behavior.

Important APIs/types/functions: `TestGoogleStorageImmutabilityProtection` and `getGcsClient`, using GCS client APIs, `gcs.Options`, and Kopia blob retention options.

Control flow: the test is skipped without immutable bucket environment/config. It creates GCS-backed storage, writes blobs with retention, verifies object retention metadata through the GCS API, extends retention, and checks deletion/immutability behavior.

State and persistence behavior: mutates real GCS bucket objects and retention settings. Objects may be undeletable until retention expires, so cleanup behavior is constrained by cloud policy.

Dependencies/integration points: exercises `gcs.PutBlob`, `ExtendBlobRetention`, GCS object retention, credentials, and shared blob semantics. Risks include cloud policy propagation delays, clock precision/truncation, environment skips, and retained test artifacts. It is the key signal for retention semantics beyond generic blob tests.
