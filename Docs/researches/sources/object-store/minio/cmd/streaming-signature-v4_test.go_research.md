# sources/object-store/minio/cmd/streaming-signature-v4_test.go

Purpose: unit tests for low-level helpers used by the signed SigV4 streaming reader.

Important APIs/types/functions under test: `readChunkLine`, `parseS3ChunkExtension`, `readCRLF`, and `parseHexUint`.

Control flow: table-driven tests validate small-buffer and overlong-line errors, unexpected EOF handling, extraction of chunk size/signature values, trimming of trailing whitespace, strict CRLF matching, invalid hex byte errors, 16-hex-digit limits, and a sweep of small integer hex encodings.

State and persistence behavior: all tests use in-memory byte readers and buffers. No HTTP request signing or object write state is created.

Dependencies/integration: protects parser helpers consumed by `s3ChunkedReader.Read` and related chunk framing logic.

Risks/test signals: the tests are precise for helper boundaries but do not construct complete signed chunk streams, verify HMAC chains, exercise signed trailers, or test the unsigned streaming reader. Regression coverage for full upload behavior relies on higher-level handler tests.
