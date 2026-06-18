# sources/user-network-fs/rclone/backend/doi/api/dataversetypes.go

Purpose: Defines the JSON response shapes consumed from Dataverse dataset APIs by the DOI backend.

Important APIs, types, and functions: `DataverseDatasetResponse` wraps status and data. `DataverseDataset` exposes `LatestVersion`. `DataverseDatasetVersion` carries `LastUpdateTime` and `Files`. `DataverseFile` combines a directory label with `DataverseDataFile` metadata. `DataverseDataFile` stores IDs, filenames, content type, file sizes, original-file fields, and MD5.

Control flow: This file has no executable control flow; fields are populated by `rest.CallJSON` in `dataverseProvider.ListEntries`.

State and persistence behavior: The structs are transient API decode models. Values are later converted into DOI `Object` instances and cached by the provider.

Dependencies and integration points: It is in package `api` and is imported by `backend/doi/dataverse.go`. JSON tags are the integration contract with Dataverse.

Risks: Schema drift or missing fields can produce zero values, affecting object size, names, MIME type, MD5, and modtime. Original-file fields override display name, size, and content type when present, so model accuracy matters for tabular or transformed files.

Test signals: No direct tests exist; Dataverse behavior is indirectly guarded only if provider integration tests are added.
