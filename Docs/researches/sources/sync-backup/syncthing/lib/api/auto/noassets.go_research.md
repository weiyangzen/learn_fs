# sources/sync-backup/syncthing/lib/api/auto/noassets.go

Purpose: Minimal fallback implementation of `auto.Assets` when built with the `noassets` tag.

Important APIs/types/functions: `Assets() map[string]assets.Asset` returns only `default/index.html` with gzipped `<html></html>` content.

Control flow: Builds a gzip buffer, flushes it, and returns a map literal.

State and persistence behavior: Stateless, in-memory asset generation on each call.

Dependencies and integration points: Satisfies the same API as generated GUI assets so API/static tests and minimal builds can run without embedding the full GUI.

Risks: The returned `Asset` does not set `Length`, `Filename`, or `Modified`, so full production serving semantics are reduced under `noassets`. It is intentionally not a complete GUI.

Test signals: `auto_test.go` passes against this fallback because it only requires gzipped default index HTML.
