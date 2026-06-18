# sources/user-network-fs/s3fs-fuse/src/nss_auth.cpp

## Purpose
Provides the NSS-backed implementation of the common s3fs cryptographic API. It supplies the library identity, NSS/NSPR initialization and teardown, HMAC-SHA1, HMAC-SHA256, MD5, and SHA256 for memory buffers and file descriptor ranges.

## Important APIs, Types, And Functions
`s3fs_crypt_lib_name()` returns `NSS`. `s3fs_init_global_ssl()` initializes NSPR with `PR_Init()` and NSS without a database using `NSS_NoDB_Init(nullptr)`. `s3fs_destroy_global_ssl()` calls `NSS_Shutdown()`, `PL_ArenaFinish()`, and `PR_Cleanup()`. Crypt mutex init/destroy are no-ops. Private `s3fs_HMAC_RAW()` creates an internal key slot, imports a symmetric HMAC key, digests data, and returns a heap digest. Public `s3fs_HMAC()` and `s3fs_HMAC256()` select SHA1 or SHA256. `s3fs_md5()`, `s3fs_md5_fd()`, `s3fs_sha256()`, and `s3fs_sha256_fd()` use `PK11_CreateDigestContext()` and `PK11_Digest*()` calls.

## Control Flow
HMAC allocation proceeds through `PK11_GetInternalKeySlot()`, `PK11_ImportSymKey()`, `PK11_CreateContextBySymKey()`, `PK11_DigestBegin()`, `PK11_DigestOp()`, and `PK11_DigestFinal()`, freeing NSS resources on each failure path. File digest functions use the same 512-byte `pread()` loop pattern as the other backends, with `size == -1` resolved by `fstat()`. Digest finalization writes into fixed-size project arrays.

## State And Persistence Behavior
Global state lives inside NSS/NSPR. Per-call NSS contexts, keys, and slots are freed before return. HMAC output is heap-owned by the caller through `unique_ptr`. The file does not persist keys, digest contexts, or output.

## Dependencies And Integration Points
Dependencies include NSS headers (`nss.h`, `pk11pub.h`, `hasht.h`), NSPR (`prinit.h`), POSIX file APIs, and project headers `common.h`, `s3fs.h`, `s3fs_auth.h`, and `s3fs_logger.h`. It is one selectable backend behind the same auth surface consumed by AWS signing and checksum code in `curl.cpp`, `common_auth.cpp`, and upload paths.

## Risks
`s3fs_md5()` and `s3fs_sha256()` do not check `PK11_CreateDigestContext()` for null before using it, so allocation/provider failure could crash. The one-shot memory digest functions do not validate null `data` or result pointers. `PK11_DigestOp()`/`PK11_DigestFinal()` return values are ignored in MD5/SHA256 helpers, so failures can be reported as success. NSS global teardown can be unsafe if other code still depends on NSS in the process.

## Test Signals
Known-vector tests should compare NSS output to OpenSSL/GnuTLS for HMAC-SHA1, HMAC-SHA256, MD5, and SHA256. Fault-injection or wrapper tests should cover digest-context creation failure and PK11 operation failures. File tests should cover invalid fd, `size == -1`, ranged hashes, and read errors.
