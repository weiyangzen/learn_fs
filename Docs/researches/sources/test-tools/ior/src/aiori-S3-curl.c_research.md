# sources/test-tools/ior/src/aiori-S3-curl.c

## Purpose
Provides a libcurl-based S3 backend named `S3-curl` for IOR and mdtest. It implements a simple object interface with configurable credentials, host, bucket, region, SSL, timeout, and certificate verification options.

## Important APIs, Types, And Functions
Defines `s3_curl_options_t`, `s3_curl_fd_t`, and `MemoryStruct`. Registers `s3_curl_aiori` with create/open/xfer/close/remove/stat/statfs/access/rename/sync hooks. Important helpers are `S3_curl_options`, `S3_curl_check_params`, `init_curl_handle`, `set_s3_url`, `S3_curl_Create`, `S3_curl_Xfer`, `S3_curl_GetFileSize`, `S3_curl_access`, and `S3_curl_stat`.

## Control Flow
`S3_curl_initialize`/`finalize` wrap libcurl global init and cleanup. Create validates options, allocates an fd, initializes a CURL easy handle, sets a PUT URL, sends a zero-length upload, and returns the fd on success. Open allocates an fd without validating remote existence. `S3_curl_Xfer` performs PUT for writes and GET for reads, checking libcurl result and HTTP status. Size and access are implemented with HEAD requests; stat synthesizes a POSIX `struct stat`; mkdir/rmdir/statfs/sync are mostly no-ops or dummy responses.

## State And Persistence Behavior
Each open fd owns a duplicated key and CURL handle. Data persists as S3 objects at `/{bucket}/{key}` on the chosen endpoint. There is no multipart state, buffering across transfers, append support, directory state, or local persistence. `hints` are stored globally but not used by this implementation.

## Dependencies And Integration Points
Uses libcurl, IOR `ior_aiori_t`, IOR logging globals, and `utilities.h`. It integrates with `aiori.c` when compiled under `USE_S3_CURL_AIORI` and with IOR's generic file lifecycle and size-check logic.

## Risks And Edge Cases
The implementation does not perform AWS Signature V4 signing; setting `CURLOPT_USERNAME` and `CURLOPT_PASSWORD` is insufficient for most S3 endpoints. Read handling is unsafe: `WriteMemoryCallback` reallocates `mem->memory`, but `S3_curl_Xfer` points it at the caller's transfer buffer, so it may realloc non-malloc memory, write beyond intended ownership, and returns the accumulated size rather than bytes copied. `ReadDataCallback` mutates the memory pointer and is unused for current write setup. The `offset` argument is ignored for both PUT and GET, so normal IOR multi-transfer files overwrite or reread whole objects rather than byte ranges. Header lists are not associated with fd lifetime but are freed after use; curl options may retain stale pointers until changed. `S3_curl_stat` treats zero-byte objects as missing.

## Test Signals
Run IOR with `-a S3-curl` against an S3-compatible test server for single-transfer whole-object writes first, then multi-transfer block-size larger than transfer-size to expose offset loss. Address sanitizer or valgrind should flag the GET realloc misuse. HEAD/access/stat tests should include zero-byte objects and missing keys.
