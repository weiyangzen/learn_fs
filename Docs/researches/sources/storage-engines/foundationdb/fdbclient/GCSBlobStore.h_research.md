# sources/storage-engines/foundationdb/fdbclient/GCSBlobStore.h

## Purpose
`GCSBlobStore.h` declares the Google Cloud Storage blob-store endpoint class. It documents that GCS uses the S3-compatible XML API for object operations but requires OAuth2 bearer-token authentication and GCS-specific project headers.

## Important APIs, Types, And Functions
`GCSBlobStoreEndpoint` derives from `S3BlobStoreEndpoint`. The constructor accepts host, service, proxy options, optional credentials, project ID, blob knobs, and extra HTTP headers. Overrides define request-header signing, secret refresh, credential JSON extraction, per-request lookup policy, credential-file key naming, resource URL serialization, and bucket creation. Public data members are `projectId`, `token`, and `lookupToken`.

## Control Flow
This header has no runtime control flow; it establishes the virtual dispatch points implemented in `GCSBlobStore.cpp`. All regular blob operations still flow through inherited S3 endpoint methods unless one of these overrides is invoked.

## State And Persistence Behavior
The class stores the current bearer token and whether that token should be refreshed from credential files on each request. It owns no local durable storage, but its methods may read credential files through the base endpoint contract and may create remote GCS buckets.

## Dependencies And Integration Points
It includes `fdbclient/S3BlobStore.h` and depends on `JSONDoc`, `HTTP::Headers`, `BlobKnobs`, `Optional<StringRef>`, and FoundationDB `Future<Void>` types through inherited declarations. It is selected by S3 blobstore URL parsing when a GCS provider parameter is present.

## Risks And Edge Cases
The public mutable `token` and `lookupToken` fields simplify tests and refresh logic but make invariant enforcement external. Because the class inherits most behavior from S3, any GCS XML API incompatibility outside auth and bucket creation would surface in inherited code rather than this header.

## Test Signals
Compile-time coverage comes from constructing and dynamic-casting `GCSBlobStoreEndpoint` in the implementation tests. Runtime signals are the GCS URL, header, credential-refresh, and bucket-create tests in `GCSBlobStore.cpp` plus integration backup/restore tests using `blobstore://...p=gcs`.
