# sources/user-network-fs/rclone/backend/doi/dataverse.go

Purpose: Implements DOI provider support for Dataverse-hosted datasets.

Important APIs, types, and functions: `activateDataverse` recognizes URLs with `persistentId`; `resolveDataverseEndpoint` builds `/api/datasets/:persistentId/`; `dataverseProvider.ListEntries` converts Dataverse dataset files into DOI `Object`s; `newDataverseProvider` wires the provider into `Fs`.

Control flow: Detection extracts `persistentId` from the resolved DOI URL. Listing first checks the backend cache, then GETs the dataset endpoint through the rclone REST client and pacer. It parses dataset `LastUpdateTime`, builds content URLs under `/api/access/datafile/{id}?format=original`, and maps each file to object remote, size, MD5, and content type, preferring original-file fields when present.

State and persistence behavior: The provider caches a slice of value-copied `Object` metadata under key `files`, then returns fresh pointers on later calls. Persistent data remains remote at Dataverse content URLs.

Dependencies and integration points: Depends on DOI `Fs`, `rest`, Dataverse API models, `path`, `url`, `time`, and rclone logging/pacer behavior. It satisfies the `doiProvider` interface consumed by `doi.go`.

Risks: A single dataset update time is used for all files. Cache invalidation is coarse and only refreshed by rebuilding or changing the session. Directory labels and original file names are joined with `path.Join`, which can normalize empty or unusual path elements. Missing MD5/content type fields surface as empty values.

Test signals: There are no Dataverse-specific tests in the listed files; behavior is analogous to the mocked Zenodo provider flow.
