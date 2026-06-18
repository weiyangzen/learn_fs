# sources/sync-backup/kopia/repo/blob/b2/b2_storage.go

Purpose: implements the deprecated Backblaze B2 blob storage provider.

Important APIs/types/functions: `b2Storage`, `GetBlob`, `resolveFileID`, `GetMetadata`, `translateError`, `PutBlob`, `DeleteBlob`, `ListBlobs`, `ConnectionInfo`, `DisplayName`, `String`, `New`, and provider `init`.

Control flow: reads validate offset, set an optional B2 byte range, download by name, skip copying for zero-length reads, and enforce output length. Metadata resolves the latest upload file ID from versions, fetches file info, and maps upload timestamp or Kopia metadata timestamp. Writes reject retention and `DoNotRecreate`, handle zero-length bodies with `http.NoBody`, upload file data with metadata, and return server mod time. Deletes hide the file and ignore not-found-like errors. Listing pages through B2 names with a prefix and emits metadata for each file. `New` warns that B2 is deprecated, validates bucket name, authenticates, opens the bucket, and wraps storage in retrying.

State and persistence behavior: blob data, metadata, and hidden-file markers persist in B2. Local state is B2 client, bucket handle, and options.

Dependencies/integration points: depends on `go-backblaze`, Kopia timestamp metadata, retrying wrapper, throttling options, and storage registry. Risks include deprecation, no retention/DoNotRecreate support, `DeleteBlob` currently returning nil even for non-not-found errors after translation, B2 version/hide semantics, and reliance on live cloud tests. Tests cover shared storage behavior and invalid bucket/blob/credentials.
