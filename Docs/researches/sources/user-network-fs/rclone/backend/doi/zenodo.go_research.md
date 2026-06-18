# sources/user-network-fs/rclone/backend/doi/zenodo.go

Purpose: Resolves Zenodo DOIs to the canonical Zenodo API record endpoint used by the shared Invenio provider.

Important APIs, types, and functions: `zenodoRecordRegex` extracts the record ID from DOI strings containing `zenodo.`. `resolveZenodoEndpoint` constructs `/api/records/{recordID}`, fetches it, and returns the `Links.Self` API URL with provider `Zenodo`.

Control flow: The resolver derives a record ID from the DOI, resolves an API URL relative to the DOI target, GETs JSON through the pacer, parses the canonical `self` link, and returns it as the endpoint.

State and persistence behavior: Stateless endpoint resolution only; the resulting endpoint is stored later in `Fs`.

Dependencies and integration points: Uses DOI API `InvenioRecordResponse`, rclone REST/pacer/retry logic, and the main DOI provider selection in `doi.go`. Listing is performed by `newInvenioProvider`.

Risks: DOI parsing depends on the `zenodo.` substring and will reject concept DOI or alternate Zenodo DOI formats if they do not match. Empty or malformed `self` links can parse into unusable endpoints unless caught by downstream calls.

Test signals: `TestZenodoRemote` covers successful record ID extraction, API record lookup, endpoint self-link handling, and subsequent listing/opening through the shared provider.
