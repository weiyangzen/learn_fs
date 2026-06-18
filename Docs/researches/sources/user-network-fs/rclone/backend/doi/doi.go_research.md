# sources/user-network-fs/rclone/backend/doi/doi.go

Purpose: Provides a read-only rclone backend for datasets addressed by DOI, resolving the DOI through a handle resolver, detecting the hosting provider, listing dataset files, and exposing HTTP downloads as rclone objects.

Important APIs, types, and functions: `Provider`, `Options`, `Fs`, `Object`, and `doiProvider` define the backend surface. `parseDoi`, `resolveDoiURL`, `resolveEndpoint`, `httpConnection`, `NewFs`, `List`, `NewObject`, `Object.Open`, `Object.Hash`, `Object.MimeType`, `Command`, and `ShowMetadata` implement core behavior.

Control flow: `NewFs` trims root, parses config, normalizes DOI input, creates an HTTP client, REST client, pacer, metadata cache, and feature set, then calls `httpConnection`. Endpoint resolution calls the DOI resolver, honors explicit provider selection, or auto-detects Dataverse, Zenodo, and Invenio. The selected provider lists all entries; if the configured root is a file, `NewFs` returns `fs.ErrorIsFile` with root adjusted to the parent. `List` filters provider entries under the current root and synthesizes directory entries. `Open` performs HTTP GET with range options and handles a non-compliant redirect by manually following `Location`.

State and persistence behavior: The backend is read-only; `Mkdir`, `Rmdir`, `Put`, `PutStream`, `Remove`, `Update`, and `SetModTime` all reject changes. Runtime state includes provider, endpoint URL, REST client root, pacer, config, and provider metadata cache.

Dependencies and integration points: Uses rclone `fs`, config, HTTP, REST, pacer, cache, hash, and provider files `dataverse.go`, `invenio.go`, and `zenodo.go`. It exposes backend commands `metadata` and `set`; `set` mutates the live options and reconnects.

Risks: Hashes advertise MD5 and return provider-supplied strings, which may be empty or malformed. Cache staleness can persist after provider-side changes. Auto-detection performs network calls and can misclassify generic Invenio-like pages. Read-only errors are plain backend errors rather than capability masking. Manual redirect handling may miss multi-hop or unusual redirect semantics.

Test signals: Internal tests cover DOI parsing and a mocked Zenodo resolver/list/download flow; `doi_test.go` wires the backend to generic fstests for a configured `TestDoi:` remote.
