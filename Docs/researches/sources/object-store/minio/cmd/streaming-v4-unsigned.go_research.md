# sources/object-store/minio/cmd/streaming-v4-unsigned.go

Purpose: decodes AWS SigV4-compatible unsigned chunked uploads, optionally with signed request authentication and declared trailers, for object and multipart handlers that accept unsigned streaming payloads.

Important APIs/types/functions: `newUnsignedV4ChunkedReader` optionally validates the request signature with `doesSignatureMatch(unsignedPayloadTrailer, ...)`, initializes declared trailers from `X-Amz-Trailer`, and returns an `s3UnsignedChunkedReader`. `s3UnsignedChunkedReader.Read` parses hex chunk sizes, enforces `maxChunkSize`, reads payloads, validates CRLF separators, and returns decoded bytes. `readTrailers` reads the terminal trailer block and only accepts keys declared in the request trailer header.

Control flow: reads first drain buffered chunk bytes, then parse a size line ending in CRLF, read exactly that many bytes, and consume the following CRLF. A zero-size chunk ends the stream and, if trailer mode is active, reads a final trailer block ending in CRLFCRLF. Trailer keys are normalized to lowercase for comparison with declared keys.

State and persistence behavior: per-reader state consists of a buffered source, optional trailer map, chunk buffer, offset, sticky error, and debug flag. No payload data is persisted here.

Dependencies/integration: shares constants and errors with `streaming-signature-v4.go`, is called from object and multipart handlers for unsigned trailer/chunked auth types, and integrates with SigV4 request authentication only when an Authorization header is present.

Risks/test signals: because payload chunks are unsigned, integrity depends on the surrounding request mode, checksums, TLS, or object-layer validation. Parser risks mirror the signed reader: chunk-size bounds, strict malformed encoding handling, and trailer allow-list enforcement. There are no dedicated tests for this file in the subset; coverage is indirect through upload handlers.
