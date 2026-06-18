# sources/user-network-fs/s3fs-fuse/src/openssl_auth.cpp

## Purpose
Provides the OpenSSL-backed implementation of the common s3fs cryptographic API. It identifies the backend, exposes no-op global initialization/teardown for modern OpenSSL, and implements HMAC-SHA1, HMAC-SHA256, MD5, and SHA256 over memory and file descriptors using the EVP API.

## Important APIs, Types, And Functions
`s3fs_crypt_lib_name()` returns `OpenSSL`. `s3fs_init_global_ssl()`, `s3fs_destroy_global_ssl()`, `s3fs_init_crypt_mutex()`, and `s3fs_destroy_crypt_mutex()` all return true. Private `s3fs_HMAC_RAW()` wraps `HMAC()` with either `EVP_sha1()` or `EVP_sha256()`. Private `s3fs_digest()` hashes memory with `EVP_MD_CTX_new()`, `EVP_DigestInit_ex()`, `EVP_DigestUpdate()`, and `EVP_DigestFinal_ex()`. Private `s3fs_digest_fd()` applies the same EVP flow to a 512-byte `pread()` loop. Public `s3fs_md5*` and `s3fs_sha256*` select the EVP digest.

## Control Flow
HMAC validates `key`, `data`, and `digestlen`, allocates `EVP_MAX_MD_SIZE`, and lets OpenSSL write the actual digest length. Memory digest helpers allocate an `EVP_MD_CTX` with RAII `unique_ptr`, return false on any EVP failure, and log OpenSSL error strings. File digesting rejects `fd == -1`, resolves `size == -1` with `fstat()`, initializes the context, updates it for each read block, stops on EOF, and finalizes into caller storage.

## State And Persistence Behavior
The OpenSSL backend relies on OpenSSL 1.1+ internal global initialization and threading. Per-call state is local and freed through RAII. Digest outputs are caller-owned arrays or `unique_ptr` buffers. There is no local persistent state.

## Dependencies And Integration Points
Dependencies include OpenSSL EVP/HMAC/ERR headers, POSIX `pread()`/`fstat()`, and `s3fs_auth.h`/`s3fs_logger.h`. It implements the same common API used by curl signing, payload hashing, common hex helpers, and multipart checksum code.

## Risks
Memory digest functions do not check null `data` or output pointers before passing them to OpenSSL. `s3fs_HMAC_RAW()` casts `keylen` to `int`; extremely large keys could truncate. `ERR_get_error()` may return zero when the failure did not populate the error queue, resulting in a null or unhelpful reason string. As with other backends, file hashing can silently hash fewer bytes if EOF occurs before the requested size.

## Test Signals
Known-vector tests should cover HMAC-SHA1, HMAC-SHA256, MD5, and SHA256, including empty input. File hashing tests should compare memory and fd hashes for full files and slices. Error-path tests should cover invalid fd, `fstat()` failure, and read errors. Cross-backend tests are valuable because the same API must behave identically across OpenSSL, NSS, and GnuTLS builds.
