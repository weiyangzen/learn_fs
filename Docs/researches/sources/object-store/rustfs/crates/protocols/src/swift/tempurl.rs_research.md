# sources/object-store/rustfs/crates/protocols/src/swift/tempurl.rs

Implements OpenStack Swift TempURL signing and validation. TempURLs allow unauthenticated, time-limited object access using account-level HMAC-SHA1 keys.

Important API surface: `TempURLParams` stores `temp_url_sig`, `temp_url_expires`, and optional `temp_url_ip_range`; `from_query()` parses them from a raw query string. `TempURL` holds the signing key and implements `generate_signature()` and `validate_request()`. `constant_time_compare()` compares signatures byte by byte. `generate_tempurl()` creates a signed URL for a path and TTL.

Control flow: validation checks current UNIX time against expiration, regenerates the expected signature from uppercased method, expiration, and path, compares signatures, and returns unauthorized errors for expired or invalid requests. Generation computes `now + ttl_seconds`, signs the path, and appends query parameters.

No local state is persisted. The key is passed into `TempURL`; in the broader Swift stack it comes from account metadata. Generated URLs embed expiration and signature in query parameters. Dependencies are Swift errors, `hmac`, `sha1`, `hex`, and `SystemTime`. The Swift handler parses query parameters, loads the account TempURL key, validates, and dispatches object operations without normal credentials.

Risks: `from_query()` splits on every `=`, does not percent-decode values, and rejects parameters containing encoded or literal `=` characters. IP range restriction is parsed but not enforced. The length mismatch path in `constant_time_compare` returns immediately, so it is not fully constant-time for different-length strings. Only SHA1 signatures are supported.

Tests cover deterministic signatures, method/path/expiration sensitivity, valid/expired/wrong-signature/method-mismatch validation, comparison behavior, query parsing, URL generation, and format checks for a documented-style test vector.
