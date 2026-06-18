# sources/sync-backup/syncthing/lib/assets/assets.go

Purpose: Utilities for serving embedded static assets over HTTP with MIME, caching, and gzip handling.

Important APIs/types/functions: `Asset` describes embedded content, compression, decompressed length, original filename, and modified time. `Serve` writes an asset with content type, ETag, Last-Modified, conditional GET support, and gzip negotiation. `MimeTypeForFile` maps common GUI extensions to stable MIME types and falls back to `mime.TypeByExtension`.

Control flow: `Serve` sets headers, checks `If-Modified-Since` and `If-None-Match`, returns 304 if matched, writes plain content directly, writes gzipped content when accepted, or decompresses gzipped content on the fly otherwise.

State and persistence behavior: Stateless. Content comes from memory; no file I/O.

Dependencies and integration points: Used by `api_statics.go` for compiled GUI assets and by generated `auto` asset bundles.

Risks: For gzipped assets, `gzip.NewReader` errors are ignored, assuming generated assets are valid. ETag is based only on modified unix seconds, so different content with the same timestamp collides. `Accept-Encoding` matching is substring-based.

Test signals: `assets_test.go` verifies gzip/plain serving, content length, MIME type, quoted ETag, and 304 behavior.
