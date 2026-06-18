<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/curl_util.h -->
# Research: sources/user-network-fs/s3fs-fuse/src/curl_util.h

Purpose: declares curl/S3 request utility functions shared by `curl.cpp` and other s3fs modules. It keeps header-list, canonicalization, URL, host, SSE-header lookup, and ETag helper prototypes out of the large transport class.

Important APIs: exposes `curl_slist_sort_insert`, `curl_slist_remove`, `get_sorted_header_keys`, `get_canonical_headers`, `get_header_value`, `MakeUrlResource`, `prepare_url`, `get_object_sse_type`, `put_headers`, `make_md5_from_binary`, `url_to_host`, `get_bucket_host`, `getCurlDebugHead`, and `etag_equals`. Forward declares `sse_type_t` and includes `metaheader.h` for `headers_t`.

Control flow surface: consumers use these helpers before signing and sending requests. `get_object_sse_type` and `put_headers` are declared here but implemented in `s3fs.cpp`, making this header part of a broader integration contract between transport utilities and filesystem/object metadata logic.

State and persistence: functions are mostly stateless by contract, but URL/host helpers read global s3fs configuration and bucket state. Header-list helpers mutate and return `curl_slist*` chains that callers own.

Dependencies/integration: includes libcurl for `curl_slist` and `curl_infotype`, C++ strings, and `metaheader.h`. `curl.cpp` depends on these declarations for signing and request setup; filesystem code can call the externally implemented SSE/header helpers without including the transport implementation.

Risks: this header exposes raw libcurl list ownership, so misuse can leak or double-free headers. Cross-file declarations for functions implemented in `s3fs.cpp` create coupling that can be missed by isolated tests of the curl module. `sse_type_t` is only forward declared, so callers needing enum values must include the defining header as well.

Test signals: compile/link tests should ensure `s3fs.cpp` provides `get_object_sse_type` and `put_headers`. Unit tests for the implementation should be paired with ownership/leak checks around the raw `curl_slist*` helpers and URL helpers under both virtual-hosted and path-request styles.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/curl_util.h -->
