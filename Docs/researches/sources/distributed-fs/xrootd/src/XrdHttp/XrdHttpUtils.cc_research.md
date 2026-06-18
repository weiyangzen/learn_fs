# sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpUtils.cc

Purpose: Implements shared HTTP utility functions for encoding, checksums, base64/hex conversion, XML escaping, HMAC redirection hashes, and xrootd/errno to HTTP status mapping.

Important APIs/types/functions: `Tobase64` overloads encode raw bytes or `vector<uint8_t>`. `base64ToBytes`, `bytesToHex`, `base64DecodeHex`, and `Fromhexdigest` convert digest forms. `calcHashes` computes an HMAC-SHA256-derived base64 hash using OpenSSL 3 `EVP_MAC` or legacy `HMAC_CTX`. `quote`, `unquote`, and `escapeXML` allocate transformed strings. `mapXrdErrToHttp`, `mapErrNoToHttp`, and `httpStatusToString` normalize errors and status text.

Control flow: Most helpers are direct transforms. `calcHashes` builds a keyed MAC over filename, request code, selected `XrdSecEntity` fields, and a timestamp string, then encodes half of the digest. Error mapping first converts xrootd protocol errors to errno, then to HTTP status.

State and persistence: Stateless except for caller-owned output buffers and malloc-returned strings. OpenSSL BIO/MAC objects are created and freed per call.

Dependencies and integration points: Depends on OpenSSL BIO/HMAC/EVP APIs, XRootD protocol and security types, and errno constants. Used by request parsing, redirects, digest handling, TPC error reporting, and static response construction.

Risks: `quote`, `unquote`, and `escapeXML` return malloc-owned buffers and require explicit `free`. `unquote` accepts percent sequences without validating hex digits. `Fromhexdigest` reserves but does not clear output, so callers should pass an empty vector or clear it first. `itos` uses `sprintf` into a fixed buffer but only for a `long`.

Test signals: Round-trip URL encoding/decoding, invalid percent and hex input, base64/hex digest conversions, OpenSSL 1.1/3 builds, HMAC stability, errno coverage, and status string fallbacks for unknown ranges.
