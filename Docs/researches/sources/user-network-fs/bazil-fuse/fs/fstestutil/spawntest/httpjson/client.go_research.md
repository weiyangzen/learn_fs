<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/fstestutil/spawntest/httpjson/client.go -->
# sources/user-network-fs/bazil-fuse/fs/fstestutil/spawntest/httpjson/client.go

Purpose: client helper for calling JSON-over-HTTP resources in tests.

Important APIs, types, and functions: exports `JSON`, `Resource`, and `(*Resource).Call`.

Control flow: `Call` marshals non-nil data as POST JSON or uses GET for nil data, sets JSON headers, executes the request with context, checks for HTTP 200, decodes JSON with unknown fields disallowed, and rejects trailing data via `mustEOF`.

State and persistence behavior: `Resource` stores an HTTP client and base URL only.

Dependencies and integration points: used by spawntest `Control.JSON` and benchmark helpers.

Risks and test signals: strict decoding can break clients if helpers add fields. Non-200 bodies are surfaced in error messages.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/fstestutil/spawntest/httpjson/client.go -->
