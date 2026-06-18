# sources/object-store/openstack-swift/swift/common/digest.py

Purpose: centralizes digest algorithm selection and client-supplied digest parsing for Swift features such as temporary URLs and checksum headers.

Important APIs/types/functions: `DEFAULT_ALLOWED_DIGESTS` names sha1, sha256, and sha512; `DEPRECATED_DIGESTS` marks sha1; `SUPPORTED_DIGESTS` is the supported set; `get_hmac` builds a newline-delimited HMAC message from request method, expiry, path, and optional `ip=<range>` prefix; `get_allowed_digests` normalizes configured algorithms, filters unsupported entries, warns on deprecated entries, and errors when nothing valid remains; `extract_digest_and_algorithm` accepts either plain hex digests or `algorithm:base64-digest` values and returns `(algorithm, hex_digest)`.

Control flow: HMAC creation first builds ordered message parts, optionally inserts IP range ahead of the method to avoid path-newline ambiguity, converts keys and parts to bytes, and delegates to `hmac.new`. Digest config handling lowercases input, defaults empty config to the supported set, subtracts unsupported algorithms, logs warnings, then returns valid and deprecated subsets. Digest extraction branches on `:`, decoding standard or URL-safe base64 when an algorithm is explicit, otherwise validates hex and infers algorithm from digest length.

State and persistence: stateless; constants are module-level policy. No persistent data is modified.

Dependencies and integration: uses `hmac`, `binascii`, and Swift `strict_b64decode`. Called by middleware and request validation paths that need compatible HMAC and digest parsing.

Risks: empty configured digest list currently allows deprecated sha1 by default; callers must enforce allowed algorithms after `extract_digest_and_algorithm`; base64 decoding pads with `==`, which is permissive by design; IP range ordering is security-sensitive for temporary URL signatures. Tests should cover allowed/deprecated logging, unsupported-only failure, hex length inference, URL-safe base64, bad base64/hex input, and HMAC compatibility with existing tempurl signatures.
