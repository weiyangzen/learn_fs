# sources/sync-backup/git-lfs/lfsapi/body.go

Purpose: Provides JSON request-body marshaling and a seekable, closable byte body for LFS API requests.

Important APIs/types/functions: `ReadSeekCloser`, `MarshalToRequest`, `NewByteBody`, and `closingByteReader.Close`.

Control flow: `MarshalToRequest` JSON-marshals an object, sets `Content-Length` header and `req.ContentLength`, then assigns a `NewByteBody` reader. `NewByteBody` wraps `bytes.Reader` with a no-op `Close`.

State and persistence behavior: Mutates the provided `http.Request` in memory. No external persistence.

Dependencies and integration points: Mirrors `lfshttp/body.go` and is used by API clients and tests that need rewindable request bodies for redirects, retries, and trace logging.

Risks and edge cases: JSON marshal failures leave request body untouched. All marshaled bodies are buffered fully in memory, which is fine for API JSON payloads but not for large object streams.

Test signals: Covered indirectly by auth and locking API tests that assert `Content-Length` and JSON payloads.
