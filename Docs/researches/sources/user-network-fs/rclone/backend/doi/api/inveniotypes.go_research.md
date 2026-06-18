# sources/user-network-fs/rclone/backend/doi/api/inveniotypes.go

Purpose: Defines JSON models for InvenioRDM and Zenodo record/file APIs used by the DOI backend.

Important APIs, types, and functions: `InvenioRecordResponse` and `InvenioRecordResponseLinks` expose the canonical record `self` URL. `InvenioFilesResponse` contains file `Entries`. Each `InvenioFilesResponseEntry` carries key, checksum, size, updated timestamp, MIME type, and content link.

Control flow: There is no logic; `invenio.go` and `zenodo.go` decode these structs from API responses.

State and persistence behavior: Instances are transient decode results and are converted into cached DOI `Object` metadata.

Dependencies and integration points: Package `api` is imported by DOI provider implementations. The checksum is later trimmed for `md5:` prefixes, and timestamp strings are parsed as RFC3339.

Risks: The checksum field may contain algorithms other than MD5; current provider code simply trims `md5:` and returns the result as MD5. Bad timestamps degrade to the unset time with a log message.

Test signals: `doi_internal_test.go` uses these types in a mock Zenodo server and verifies listing, size, content, MD5, and MIME type.
