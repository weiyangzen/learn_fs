# sources/sync-backup/kopia/repo/blob/gcs/gcs_storage.go

Purpose: implements Kopia blob storage on Google Cloud Storage.

Important APIs/types/functions: `gcsStorage`, `GetBlob`, `getBlobWithVersion`, `GetMetadata`, `getBlobMeta`, `translateError`, `PutBlob`, `DeleteBlob`, `ExtendBlobRetention`, `ListBlobs`, `ConnectionInfo`, `DisplayName`, `Close`, `toBlobID`, `New`, and provider `init`.

Control flow: reads validate offset, optionally select an object generation, open a range reader, copy contents, and verify exact length. Metadata reads object attributes and maps Kopia timestamp metadata. Writes apply `DoesNotExist` precondition for `DoNotRecreate`, set chunk size/content type/timestamp metadata, optionally set locked object retention, copy data to the writer, cancel/close correctly on copy errors, commit on close, and return writer update time. Deletes ignore not-found. Retention extension updates object retention with second-truncated retain-until time. Listing iterates bucket objects by prefix and emits metadata. `New` creates a client with credentials/defaults, opens a bucket handle, optionally wraps PIT/readonly and retrying, and verifies listing.

State and persistence behavior: object bytes, metadata, generations, and retention live in GCS. The provider stores client/bucket/options and closes the client on `Close`.

Dependencies/integration points: uses `cloud.google.com/go/storage`, Google API errors, timestamp metadata, retrying wrapper, PIT wrapper, and registry. Risks include exact length checks with GCS range semantics, precondition mapping, retention permission requirements, timestamp metadata key casing, and cloud environment skips. Tests cover shared storage behavior, invalid config, cleanup, immutability, and versioned PIT.
