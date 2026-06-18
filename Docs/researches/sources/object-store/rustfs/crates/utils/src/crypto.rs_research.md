# sources/object-store/rustfs/crates/utils/src/crypto.rs

Purpose: Crypto encoding and digest helpers for base64url, hex, HMAC, and SHA-256.

Important APIs: `base64_encode_url_safe_no_pad`, `base64_decode_url_safe_no_pad`, `hex`, `is_sha256_checksum`, `hmac_sha1`, `hmac_sha256`, `hex_sha256`, and `hex_sha256_chunk`.

Control flow: Base64 uses SIMD URL-safe no-padding codec. Hex uses `hex_simd` lowercase. SHA-256 helpers compute fixed 32-byte digest, encode into a stack `MaybeUninit` buffer via `hex_simd`, and pass the temporary string to a caller closure to avoid allocation. Chunk hashing updates a single hasher across `hyper::body::Bytes` slices.

State and dependencies: Stateless. Depends on `base64-simd`, `hex-simd`, `hmac`, `sha1`, `sha2`, and `hyper::body::Bytes`.

Integration points: Enabled by utils `crypto` feature and likely used by signing/checksum paths.

Risks and tests: HMAC constructors unwrap, though HMAC accepts arbitrary key lengths for these algorithms. Closure-based hex APIs require consumers not to retain borrowed string beyond callback. Tests cover base64 round trip and strict lowercase SHA-256 checksum validation.
