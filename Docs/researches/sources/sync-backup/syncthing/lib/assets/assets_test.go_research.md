# sources/sync-backup/syncthing/lib/assets/assets_test.go

Purpose: Unit tests for embedded asset serving behavior.

Important APIs/types/functions: Helpers `compress` and `decompress` create and inspect gzip content. `TestServe` and `TestServeGzip` call `testServe` for plain and gzipped asset paths.

Control flow: The test handler serves a synthetic `index.html`. It requests with and without gzip support, validates OK status, content type, quoted ETag, content length matching actual encoded body length, decoded body content, and conditional 304 responses for ETag and Last-Modified.

State and persistence behavior: In-memory only, using `httptest`.

Dependencies and integration points: Directly validates `assets.Serve` and indirectly protects `api_statics.go` serving behavior.

Risks: Tests use a simple HTML asset and do not cover every MIME type, malformed gzip, or fallback `mime.TypeByExtension`.

Test signals: Strong signal for HTTP caching and gzip negotiation correctness.
