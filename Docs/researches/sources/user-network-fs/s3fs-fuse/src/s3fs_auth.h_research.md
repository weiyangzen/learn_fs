# sources/user-network-fs/s3fs-fuse/src/s3fs_auth.h

## Purpose

This header declares the cryptographic and digest primitives used by s3fs authentication, payload hashing, and request signing. It abstracts the concrete crypto backend behind a stable set of functions for MD5, SHA-256, HMAC, SSL/global crypto initialization, and crypto mutex lifecycle. The implementation is split across common auth code and backend-specific auth files.

## Important APIs, Types, and Functions

- `using md5_t = std::array<unsigned char, 16>` and `using sha256_t = std::array<unsigned char, 32>` define fixed-size binary digest containers.
- `s3fs_get_content_md5(int fd)`: declared as a common auth helper that computes the Content-MD5 representation for a file descriptor.
- `s3fs_sha256_hex_fd(int fd, off_t start, off_t size)`: common helper that returns a hex SHA-256 digest over a file descriptor range.
- `s3fs_crypt_lib_name()`: reports the active crypto library/backend name; `s3fs.cpp` uses this in startup logging.
- `s3fs_init_global_ssl()` and `s3fs_destroy_global_ssl()`: initialize and tear down global SSL/crypto library state around curl/FUSE process lifetime.
- `s3fs_init_crypt_mutex()` and `s3fs_destroy_crypt_mutex()`: manage backend mutex support, typically relevant for crypto libraries or versions requiring explicit thread-safety callbacks.
- `s3fs_HMAC()` and `s3fs_HMAC256()`: compute HMAC digests using caller-provided key/data buffers and return owned byte arrays plus digest length.
- `s3fs_md5()`, `s3fs_md5_fd()`, `s3fs_sha256()`, and `s3fs_sha256_fd()`: compute binary MD5 or SHA-256 digests for memory buffers or file descriptor ranges.

## Control Flow

This file contains declarations only. The expected process flow is: startup initializes global SSL/crypto state before curl/S3 operations, request-signing code calls HMAC and SHA-256 helpers as needed, upload code can compute MD5/SHA-256 over file contents or ranges, and shutdown destroys curl and then global SSL/crypto state. `s3fs.cpp` follows that lifecycle by calling `s3fs_init_global_ssl()` before `S3fsCurl::InitS3fsCurl()` and `s3fs_destroy_global_ssl()` after destroying curl.

## State and Persistence Behavior

The header declares functions that may manage global crypto/SSL state and mutex state in their implementations, but it defines no state itself. Digest functions operate on caller-provided buffers or file descriptors and return computed digests; they do not persist data. The `unique_ptr<unsigned char[]>` return values make ownership explicit for HMAC result buffers.

## Dependencies and Integration Points

The header depends on `<array>`, `<memory>`, `<string>`, and `<sys/types.h>` for digest containers, owned buffers, string return values, and `off_t`. It is included by `s3fs.cpp` for crypto backend reporting and SSL lifecycle, and it is likely included by curl/auth/signing modules that need SigV2/SigV4 HMACs, payload hashes, SSE-C key checks, or Content-MD5 generation.

The comments indicate a split implementation: common file-descriptor digest helpers live in `common_auth.cpp`, while backend-specific functions live in `xxxxxx_auth.cpp` implementations, such as OpenSSL or alternative crypto-library adapters.

## Risks and Edge Cases

The API returns null-like `unique_ptr` values or `bool` status for failures, so callers must consistently check results and digest lengths. File-descriptor digest functions accept `off_t start` and `off_t size`; implementations must preserve the fd offset or document changes, handle negative/overflowing ranges, partial reads, EINTR, sparse files, and very large objects. Global SSL lifecycle ordering matters: destroying SSL before curl or worker threads finish using crypto would be unsafe. Thread-safety mutex setup must match the selected backend's requirements.

MD5 remains present because S3 uses Content-MD5 and SSE-C key MD5 workflows, but it is not collision-resistant for general integrity decisions. Callers should prefer SHA-256/HMAC-SHA256 for authentication and signing where the protocol allows it.

## Test Signals

Unit tests should verify MD5 and SHA-256 against known vectors for memory buffers and fd ranges, including empty input, partial ranges, unaligned offsets, and large files. HMAC and HMAC-SHA256 should be checked against standard test vectors and should validate digest length outputs. Lifecycle tests should call init/destroy repeatedly where supported and run digest/HMAC work concurrently under thread sanitizer or equivalent. Integration tests should validate SigV4 signing, Content-MD5 upload headers, unsigned-payload mode, and SSE-C metadata/key-MD5 behavior against a local S3-compatible service.
