<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/common_auth.cpp -->
# Research: sources/user-network-fs/s3fs-fuse/src/common_auth.cpp

Purpose: small authentication/hash helper implementation for computing request payload hashes used by S3 HTTP headers and AWS signature generation.

Important APIs: `s3fs_get_content_md5(int fd)` computes an MD5 digest over an entire file descriptor and returns base64. `s3fs_sha256_hex_fd(int fd, off_t start, off_t size)` computes a SHA-256 digest over a file descriptor range and returns lowercase hex.

Control flow: each function delegates to lower-level crypto/file helpers from `s3fs_auth.h`, checks the boolean success result, returns an empty string on failure, and encodes the raw digest via `s3fs_base64` or `s3fs_hex_lower` from `string_util.h`.

State and persistence: stateless except for reading from the supplied file descriptor. No persistent data is written. Callers treat an empty string as failure; in `curl.cpp`, this maps to `-EIO` for MD5/SHA256 setup failures.

Dependencies/integration: used by `S3fsCurl::PutRequest` for `Content-MD5` and by Signature V4 payload hash calculation for full PUTs and multipart parts. Depends on digest typedefs (`md5_t`, `sha256_t`) and helpers `s3fs_md5_fd`, `s3fs_sha256_fd`, `s3fs_base64`, and `s3fs_hex_lower`.

Risks: empty string conflates digest failure with a theoretically empty textual result, though these encodings are never empty for valid hashes. Hash helpers must preserve file descriptor offsets or callers must reset around them; `curl.cpp` separately duplicates/rewinds file descriptors for upload. Large-file hashing is synchronous and can be expensive before upload.

Test signals: verify MD5/base64 and SHA256/hex against known files, partial ranges, zero-length ranges, invalid descriptors, and descriptor-offset behavior. Curl request tests should confirm failures propagate to `-EIO` and successful hashes appear in signing/header paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/common_auth.cpp -->
