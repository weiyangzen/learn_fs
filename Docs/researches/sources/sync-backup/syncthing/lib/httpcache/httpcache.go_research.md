# sources/sync-backup/syncthing/lib/httpcache/httpcache.go

## Purpose
Implements an in-memory HTTP middleware cache for a single path/response, including precomputed gzip output.

## Important APIs, Types, and Functions
`SinglePathCache`, constructor `SinglePath`, `recordedResponse`, `responseRecorder`, `ServeHTTP`, and `serveCached`.

## Control Flow
Only GET and HEAD use caching; other methods pass through. Requests first attempt cached response under an RLock, then retry under a write lock to avoid duplicate fills. On miss, the child request is cloned with `Accept-Encoding` removed, the next handler is recorded, successful 200 responses are gzipped and stored, then the recorded response is served to the client.

## State and Persistence Behavior
Stores one response in memory with status, headers, plain bytes, gzip bytes, creation time, and keep duration. No disk persistence.

## Dependencies and Integration Points
Uses `net/http`, `compress/gzip`, and standard locking. Intended for endpoints where one cached representation is valid for all GET/HEAD callers.

## Risks
The cache key ignores path, query string, request headers, and user/session identity; it is safe only behind a single-path/public-response contract. HEAD responses are served with a body because `recordedResponse.ServeHTTP` does not suppress writes. Header maps are assigned directly to the response writer.

## Test Signals
No tests in this subset; useful tests would cover GET/HEAD, gzip/plain responses, expiration, non-200 pass-through, and concurrency.
