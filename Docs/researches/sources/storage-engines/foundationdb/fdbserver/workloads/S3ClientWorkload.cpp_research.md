# sources/storage-engines/foundationdb/fdbserver/workloads/S3ClientWorkload.cpp

## Purpose
`S3ClientWorkload` validates FoundationDB blob/S3 client upload, download, delete, credential discovery, and optional mock-S3 fault injection in simulation. It uploads a generated credentials file to a blob URL, downloads it, compares bytes, and cleans local and remote artifacts.

## Important APIs, Types, And Functions
The workload derives from `TestWorkload` and registers as `S3ClientWorkload`. Important methods are `setupCredentialsFile`, `addFileToUrl`, `start`, and `_setup`. It uses `copyUpFile`, `copyDownFile`, `deleteResource`, `S3BlobStoreEndpoint::fromString`, `MockS3Server`, `MockS3ServerChaos`, `S3FaultInjector`, global `INetwork::enBlobCredentialFiles`, and platform file helpers.

## Control Flow
Setup on client 0 registers a mock S3 HTTP handler when the URL points to localhost, optionally using the chaos server, and all clients configure fault rates when chaos is enabled. `start` runs only on client 0, disables bulk-loading connection failures in simulation, pre-cleans stale files, creates a deterministic per-run directory under `simfdb`, writes credentials, builds a unique object URL, uploads, downloads, deletes the remote object, compares downloaded content, then deletes local files and the run directory.

## State And Persistence Behavior
The workload writes a credentials JSON file in a per-run simulation directory and registers that path in network-global blob credential file state. It creates and deletes one remote S3 object. Local cleanup is best-effort after success and after upload failures.

## Dependencies And Integration Points
It integrates with FoundationDB's blobstore URL parser, backup/S3 credential handling, simulator HTTP handlers, mock S3 persistence, chaos fault injector, and platform filesystem APIs. It also disables a class of connection failures because network partitions between cluster controller and data distributor can prevent unrelated bulk-loading tasks from completing.

## Risks And Edge Cases
The URL manipulation must preserve resources and query strings; malformed base URLs throw `backup_invalid_url`. Cleanup errors are non-fatal except for the original transfer error. The `pass` field is initialized true and the destructor logs pass/fail, but the file does not set `pass=false` on caught errors before throwing, so destructor traces may not fully encode failure state.

## Test Signals
Transfer errors emit `S3ClientWorkloadError`, URL parse failures emit `S3ClientWorkloadURLParseError`, byte mismatches emit `S3ClientWorkloadContentMismatch`, and cleanup paths emit debug or warning traces. `check` returns true; actor failure is the primary signal.
