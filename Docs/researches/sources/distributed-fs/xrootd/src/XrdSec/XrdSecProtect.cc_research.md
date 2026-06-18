# sources/distributed-fs/xrootd/src/XrdSec/XrdSecProtect.cc

Purpose: Implements XRootD request stream protection by deciding which requests require signatures, creating `kXR_sigver` requests, and verifying received signatures.

Important APIs and functions: `Screen` evaluates request codes against `secTable` and conditional rules for `open`, `query`, and `set`. `Secure` hashes sequence number, request header, and optional payload, encrypts or sends the SHA-256 digest, and builds a `SecurityRequest`. `Verify` checks anti-replay sequence order, stream id, request id, signature version, hash/key flags, decrypts if needed, recomputes the digest, and compares. `SetProtection` maps protocol response levels and overrides into an active security vector.

Control flow: Callers first use `NEED2SECURE(protP)(request)` to avoid unnecessary signing. When signing, `Secure` increments the local sequence, signs the header and, depending on request/data policy, payload bytes. On the server side, `Verify` validates metadata before digest comparison and records the accepted sequence.

State and persistence: Each `XrdSecProtect` holds the auth protocol pointer, selected security vector, protocol response copy, sequence number union, data-signing flag, and encryption-permitted flag. No durable state exists.

Dependencies and integration points: Uses `XProtocol` request structs, OpenSSL EVP SHA-256 or CommonCrypto headers, `XrdSecProtocol::Encrypt/Decrypt/getKey`, `XrdSecProtector`, atomics/platform helpers, and errno-to-text conversion.

Risks: Sequence numbers are per object and must not be shared across independent streams. The anti-replay compare relies on network byte order preserving monotonic comparison. If `force` permits unencrypted hashes, signatures provide integrity only against parties without stream write access assumptions. Payload signing is skipped for write/pgwrite unless `secVerData` is enabled. `EVP_get_digestbyname("sha256")` is not checked for null.

Test signals: Sign/verify every level, conditional open/query/set cases, payload and `kXR_nodata` behavior, replayed and out-of-order sequence numbers, stream/request mismatch, unsupported crypto flags, protocols with and without session keys, and malformed signature lengths.
