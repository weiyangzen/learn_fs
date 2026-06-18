# sources/user-network-fs/rclone/backend/doi/invenio.go

Purpose: Implements DOI provider detection and file listing for InvenioRDM-compatible repositories, also reused for Zenodo after endpoint resolution.

Important APIs, types, and functions: `activateInvenio`, `resolveInvenioEndpoint`, `checkInvenioAPIURL`, `invenioProvider.ListEntries`, and `newInvenioProvider` are the main surfaces. `invenioRecordRegex` extracts record IDs from resolved URLs.

Control flow: Endpoint resolution first GETs the resolved DOI URL, scans `Link` headers for a linkset API URL, validates it with `checkInvenioAPIURL`, and falls back to guessing `/api/records/{id}` from the final request URL. Listing checks the provider cache, GETs `{endpoint}/files`, parses RFC3339 update times, strips an `md5:` checksum prefix, and creates DOI `Object` entries using content links.

State and persistence behavior: File metadata is cached under `files` as value copies, then returned as new pointers. No remote data is mutated.

Dependencies and integration points: Uses `parseLinkHeader` from `link_header.go`, Invenio API models, rclone REST/pacer/retry logic, and DOI `Fs`. Zenodo uses this provider after resolving the canonical Zenodo endpoint.

Risks: Link header parsing is simple and comma-splits without full RFC quoting support. Endpoint guessing depends on URL path shape. Cache staleness is not time-bounded. Non-MD5 checksums may be misreported as MD5 after prefix trimming if provider behavior changes.

Test signals: Mock Zenodo tests cover the shared Invenio file-listing structure; link header parsing has its own unit test.
