## sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpChecksumHandler.cc

Purpose: implements checksum algorithm configuration and negotiation for HTTP `Want-Digest` and `Want-Repr-Digest` headers.

Important APIs and control flow: `configure()` initializes a static map of supported algorithms, then parses the configured checksum list. `initializeCksumsMaps()` registers md5, adler32/adler, sha1/sha-256/sha-512, UNIX cksum, crc32, and crc32c mappings. `initializeXRootDConfiguredCksums()` parses config entries like `0:adler32`, stores HTTP-compatible configured checksum pointers, and records non-IANA/unknown names. `getChecksumToRunWantDigest()` lowercases and strips q-values from user digests, returns the first configured checksum requested by the client, or the first configured checksum as fallback. `getChecksumToRunWantReprDigest()` chooses the configured checksum with the highest client preference, defaulting to the first configured entry.

State and persistence: static `XROOTD_DIGEST_NAME_TO_CKSUMS` owns checksum objects; each handler instance stores raw pointers into that map plus unknown configured names. There is no durable state.

Dependencies and integration: used by HTTP request handling to decide which XRootD checksum command to run and how to name the HTTP response digest. It relies on `XrdOucTUtils::splitString()` and `XrdOucUtils::trim()`.

Risks and test signals: repeated `configure()` appends to instance vectors without clearing and reinitializes static maps; tests should check idempotence expectations. `getElement(..., position)` assumes the split has enough elements, so malformed config or q-value strings can throw/out-of-range depending split behavior. Tests should cover malformed config, duplicate aliases, adler32 adding both adler32 and adler, unknown algorithms, case-insensitive Want-Digest, and tie behavior for Want-Repr-Digest map ordering.
