## sources/object-store/garage/src/api/common/signature/streaming.rs

Purpose: parses AWS aws-chunked streaming request bodies, verifies per-chunk signatures, handles trailer checksums, and produces `ReqBody`.

Important APIs/types/functions: `parse_streaming_body`, `StreamingPayloadError`, `StreamingPayloadChunk`, `StreamingPayloadStream<S>`, private payload parsers for chunk/trailer headers, `compute_streaming_payload_signature`, and `compute_streaming_trailer_signature`.

Control flow: streaming content modes remove `aws-chunked` from `Content-Encoding`, validate trailer and signing combinations, prepare trailer checksum calculation, and build signing state from seed signature/key/date/scope. `StreamingPayloadStream::poll_next` buffers incoming bytes, parses chunk headers/data/trailers with nom, verifies signatures against the previous signature, emits data frames, emits trailer frames, and stops on zero-sized chunk or trailer.

State/persistence: per-request buffer, signing state, checksummer, and trailer metadata only.

Dependencies/integration: called by `signature::verify_request`; output consumed by body/checksum handlers. Depends on `body_stream`, checksum header parsing, HMAC, SHA256, nom, and hyper frames.

Risks: parser correctness is security-sensitive. Content-Encoding cleanup tolerates absent headers for minio compatibility but rejects non-aws-chunked streaming encodings if a header was present. Unexpected EOF and bad signatures become bad requests. Only a single trailer header is represented in the emitted trailer map.

Test signals: local async test covers interrupted signed payload stream returning `Unexpected EOF`.
