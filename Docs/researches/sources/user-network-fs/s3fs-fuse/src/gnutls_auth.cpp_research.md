# sources/user-network-fs/s3fs-fuse/src/gnutls_auth.cpp

## Purpose
Provides the GnuTLS-backed implementation of the common s3fs cryptographic API declared in `s3fs_auth.h`. It supplies library identity, global crypto initialization/teardown, HMAC-SHA1, HMAC-SHA256, MD5, and SHA256 over memory buffers and file descriptors. It supports two build variants: GnuTLS with nettle primitives or GnuTLS with libgcrypt.

## Important APIs, Types, And Functions
`s3fs_crypt_lib_name()` returns either `GnuTLS(nettle)` or `GnuTLS(gcrypt)`. `s3fs_init_global_ssl()` calls `gnutls_global_init()` and, in the gcrypt variant, `gcry_check_version()`. `s3fs_destroy_global_ssl()` calls `gnutls_global_deinit()`. Crypt mutex init/destroy are no-ops. `s3fs_HMAC()` computes SHA1 HMAC and `s3fs_HMAC256()` computes SHA256 HMAC. `s3fs_md5()` and `s3fs_sha256()` hash memory; `s3fs_md5_fd()` and `s3fs_sha256_fd()` hash a range of a file descriptor using 512-byte `pread()` loops.

## Control Flow
Compile-time `USE_GNUTLS_NETTLE` selects nettle contexts (`hmac_sha1_ctx`, `hmac_sha256_ctx`, `md5_ctx`, `sha256_ctx`) or GnuTLS/libgcrypt APIs (`gnutls_hmac_fast`, `gcry_md_open`, `gcry_md_write`, `gcry_md_read`). File hashing treats `size == -1` as "hash the whole file" after `fstat()`. Each loop computes the next read length as `min(512, size - total)`, reads at `start + total`, stops on EOF, returns false on read errors, and finalizes the digest into project fixed-size arrays.

## State And Persistence Behavior
Global state belongs to GnuTLS and optionally libgcrypt. Per-call digest contexts are stack or library handles and are closed before return. HMAC returns heap-owned buffers via `std::unique_ptr<unsigned char[]>`; callers receive digest length through `digestlen`. No secrets or digests are persisted by this file.

## Dependencies And Integration Points
This file depends on GnuTLS, optionally nettle or gcrypt, POSIX `pread`/`fstat`, and project headers `common.h`, `s3fs.h`, `s3fs_auth.h`, and `s3fs_logger.h`. The common API is used by `curl.cpp` for AWS signature v2/v4 HMAC derivation and payload hashing, by multipart upload code for MD5/ETag work, and by `common_auth.cpp`/`curl_util.cpp` for hex digest helpers.

## Risks
The nettle `s3fs_sha256_fd()` path does not implement the `size == -1` whole-file convention that the gcrypt, NSS, and OpenSSL paths implement; a caller passing `-1` would skip the loop and return the digest of an empty stream. Some memory hashing functions do not validate null `data` or result pointers, so callers must honor the API. The read loop stops on short EOF without treating it as an error, which is acceptable for changing files only if callers can tolerate hashing fewer bytes. Digest buffers in gnutls-fast HMAC allocate `len + 1` though the extra byte is not used as a terminator.

## Test Signals
Cross-backend tests should compare HMAC-SHA1, HMAC-SHA256, MD5, and SHA256 against known vectors for all configured crypto libraries. File hashing tests should cover full-file `size == -1`, ranged hashing with nonzero `start`, zero-length input, invalid fd, and a short/truncated file. A specific regression test should assert nettle SHA256 fd hashing honors whole-file behavior if that path is fixed.
