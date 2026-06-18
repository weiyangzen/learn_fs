# sources/object-store/minio/cmd/streaming-signature-v4.go

Purpose: validates and decodes AWS S3 Signature V4 streaming chunked uploads, including signed trailers, into a normal payload reader for object and multipart PUT paths.

Important APIs/types/functions: constants define streaming payload markers, chunk-signing algorithms, `aws-chunked` encoding, trailer header names, and parser limits. `calculateSeedSignature` verifies the request authorization header and seed signature. `newSignV4ChunkedReader` constructs an `s3ChunkedReader`. `s3ChunkedReader.Read` parses chunk sizes and `chunk-signature` extensions, enforces `maxChunkSize`, reads payload bytes, computes SHA-256, validates chained HMAC signatures, handles the final zero-size chunk, and optionally reads trailers. Helpers include `getChunkSignature`, `getTrailerChunkSignature`, `readTrailers`, `readCRLF`, `readChunkLine`, `parseS3ChunkExtension`, `parseChunkSignature`, and `parseHexUint`.

Control flow: the seed signature is checked first using canonical SigV4 request construction and the expected streaming payload hash. Each read drains any buffered chunk data before parsing a new chunk. Chunk signatures chain by replacing `seedSignature` with the previously verified signature, so any tampered chunk breaks all subsequent verification. Trailer mode pre-populates `req.Trailer` only with names declared in `X-Amz-Trailer`, then `readTrailers` verifies the trailer-signature chunk and rejects undeclared or missing trailers.

State and persistence behavior: all state is per-reader: credentials, seed date/region/signature, requested trailers, a reusable chunk buffer, hash writer, offset, and sticky error. No data is persisted; decoded bytes flow into object-layer write paths.

Dependencies/integration: used by object and multipart handlers for `authTypeStreamingSigned` and `authTypeStreamingSignedTrailer`. It integrates with SigV4 parsing/auth helpers, MinIO credentials, `globalSite.Region`, S3 service signing keys, SHA-256, HTTP request trailers, and API error codes.

Risks/test signals: this is security-sensitive parsing. Boundary risks include accepting malformed chunk framing, allowing chunks above 16 MiB, trailer canonicalization mismatches, case handling for declared trailer names, and sticky error behavior after partial reads. Unit tests cover helper parsing (`readChunkLine`, extension parsing, CRLF, and hex parsing), while full signed streaming behavior is exercised indirectly through S3 handler tests.
