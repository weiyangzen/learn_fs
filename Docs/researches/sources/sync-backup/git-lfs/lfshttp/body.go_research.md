# sources/sync-backup/git-lfs/lfshttp/body.go

Purpose: Provides JSON body marshaling and a seekable/closable byte body for HTTP client requests.

Important APIs/types/functions: `ReadSeekCloser`, `MarshalToRequest`, `NewByteBody`, and `closingByteReader.Close`.

Control flow: JSON-marshals input, sets `Content-Length`, assigns `ContentLength`, and wraps bytes in a `bytes.Reader` that implements `Close`.

State and persistence behavior: Mutates only the passed `http.Request`; no external state.

Dependencies and integration points: Used by `lfshttp.Client.NewRequest`, retry logic, verbose tracing, and tests. Seekability is required because tracing and retry/redirect handling rewind bodies.

Risks and edge cases: Fully buffers JSON payloads in memory. Non-JSON or large streaming bodies should not use this helper.

Test signals: `client_test.go`, `retries_test.go`, and verbose/stats tests exercise body creation and rewinding indirectly.
