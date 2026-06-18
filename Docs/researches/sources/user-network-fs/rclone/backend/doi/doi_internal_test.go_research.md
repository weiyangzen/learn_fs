# sources/user-network-fs/rclone/backend/doi/doi_internal_test.go

Purpose: Unit-tests DOI parsing and exercises the DOI backend against mocked resolver and Zenodo/Invenio-style APIs.

Important APIs, types, and functions: `TestParseDoi` covers accepted DOI forms. `prepareMockDoiResolverServer` emits handle API responses. `prepareMockZenodoServer` serves record metadata, file listings, and file contents. `md5Sum` helps populate API checksums. `TestZenodoRemote` verifies listing, object lookup, hash, open, and MIME type.

Control flow: The mock resolver returns a URL for the DOI. The mock Zenodo server returns a canonical record `self` URL, file entries with content URLs, and content bytes. `TestZenodoRemote` constructs `NewFs` with explicit provider `zenodo`, lists entries, sorts them, asserts object metadata, opens both files, and compares downloaded bytes.

State and persistence behavior: All state is in httptest servers and in-memory maps. Servers are closed with `t.Cleanup`. The backend's metadata cache is naturally exercised by repeated list/object operations.

Dependencies and integration points: Uses `httptest`, `encoding/json`, rclone `configmap`, `hash`, `fs.MimeTyper`, and the DOI API model structs. It tests network-facing provider code without external services.

Risks: The parse test comment for `dx.doi.org` uses `https://dxdoi.org/...`, which still passes because the hostname suffix is `doi.org`; this may obscure intended coverage. The mock checksum omits the `md5:` prefix commonly seen in Invenio responses, so trimming logic is only partially covered.

Test signals: Passing tests show DOI normalization, resolver requests with `index=1`, Zenodo endpoint derivation, provider file listing, MD5 propagation, MIME type propagation, and file download behavior.
