<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/curl.h -->
# Research: sources/user-network-fs/s3fs-fuse/src/curl.h

Purpose: public and private interface for `S3fsCurl`, the libcurl-backed S3 transport wrapper. It exposes configuration knobs, request methods, response accessors, and compatibility shims for libcurl options that may be absent at compile time.

Important APIs/types: defines `curlprogress`, `CurlUniquePtr`, `s3fscurl_lazy_setup`, `sseckeymap_t`, and `sseckeylist_t`. The private `REQTYPE` enum class classifies every request flavor for signing, retry reconstruction, and setup logic. Static setters/getters control certificate checking, timeouts, retries, public bucket mode, ACL, storage class, SSE, content MD5, verbose/debug body, hostname verification, SSL client certs, multipart sizes, signature mode, unsigned payload, user agent, ListObjectsV2, requester pays, proxy, and IP resolution. Public methods implement IAM, object, bucket, and multipart operations.

Control flow surface: callers initialize global curl and credentials once, then construct `S3fsCurl` objects for request batches. Per-request methods populate internal fields and either perform immediately or expose pre-setup/lazy setup for parallel multipart workers. `RequestPerform` is the common execution path. Response data is retrieved through `GetResponseCode`, `GetCurlErrorString`, `GetResponseHeaders`, `GetBodyData`, `GetHeadData`, and related accessors.

State and persistence: declares extensive static process-wide configuration and per-instance request state. The handle is stored as `CurlUniquePtr` protected by `curl_handles_lock`; `curl_progress` maps raw handles to timeout progress records. Per-request members retain raw `curl_slist*` headers and raw pointers into strings or file buffers for upload bodies, so object lifetime and retry backup fields matter. Remote persistence occurs only when implementation request methods hit S3.

Dependencies/integration: includes libcurl, `common.h`, `metaheader.h`, `s3fs_util.h`, and `types.h`. Forward-declares `S3fsCred` to avoid exposing credential implementation. Compatibility macros map newer libcurl options to numeric placeholders so older build environments can compile and fail gracefully at runtime.

Risks: the class mixes global configuration, low-level handle management, signing, and high-level S3 operations, so changes can have broad blast radius. Static mutable state is not generally synchronized except curl handle/progress tracking. Raw `curl_slist*` ownership is manual and must be cleared on all paths. The lazy setup function pointer is powerful but requires each setup method to leave the object in a complete, retryable state.

Test signals: compile against older and newer libcurl headers to exercise compatibility macros. API-level tests should validate each setter/getter old-value behavior, initialization failure paths, per-request type transitions, header cleanup after repeated requests on one object, and lazy multipart setup followed by `RequestPerform`/completion.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/curl.h -->
