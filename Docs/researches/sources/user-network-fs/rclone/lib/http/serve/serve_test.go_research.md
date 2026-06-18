# sources/user-network-fs/rclone/lib/http/serve/serve_test.go

Source read signal: reviewed complete local file (106 lines, sha256 ae5c730bbc4a90bc).

Purpose: Tests HTTP object serving semantics for methods, headers, range requests, metadata, and response body.

Important APIs/types/functions: Tests `TestObjectBadMethod`, `TestObjectHEAD`, `TestObjectGET`, `TestObjectRange`, `TestObjectBadRange`, and `TestObjectHEADMetadata`.

Control flow: Uses `httptest` requests/recorders and mock or memory objects, then asserts status, content length, accept-ranges, last-modified, content-range, body, and metadata headers.

State and persistence behavior: In-memory objects only; no persistent writes.

Dependencies and integration points: Uses `mockobject`, `object.NewMemoryObject`, `fs.Metadata`, and standard HTTP test tools.

Risks and test signals: Good coverage for basic and range behavior. It does not simulate streaming write errors or object-open failures after headers are prepared.
