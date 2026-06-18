<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/curl_util.cpp -->
# Research: sources/user-network-fs/s3fs-fuse/src/curl_util.cpp

Purpose: utility implementation for S3/libcurl request construction: sorted header-list manipulation, AWS canonical-header formatting, bucket URL transformation, host extraction, MD5 helper, curl debug labels, and ETag comparison.

Important APIs: `curl_slist_sort_insert` inserts or replaces a header in case-insensitive sorted order; `curl_slist_remove` deletes matching headers; `get_sorted_header_keys`, `get_header_value`, and `get_canonical_headers` support Signature V2/V4 signing; `MakeUrlResource` builds encoded S3 resource paths and base URLs; `prepare_url` converts service-path URL form into virtual-hosted or path-style request URLs; `make_md5_from_binary` computes base64 MD5; `url_to_host` and `get_bucket_host` support host headers; `getCurlDebugHead` labels curl debug traffic; `etag_equals` compares quoted/unquoted ETags case-insensitively.

Control flow: header insertion trims key/value, allocates a new `curl_slist` node with `malloc`, walks the sorted list, replaces on equal key, or inserts before the first greater key. Canonicalization walks the sorted list, drops empty-value headers because libcurl discards them, lowercases keys, trims values, and optionally filters to `x-amz` headers. URL construction encodes `service_path + bucket + realpath`, appends it to `s3host`, then `prepare_url` rewrites into either `bucket.host/path` virtual-hosted style or `host/bucket/path` path-request style. Host extraction requires `http://` or `https://` and aborts on invalid schemes.

State and persistence: no owned persistent state. Functions read global configuration (`service_path`, `s3host`, `pathrequeststyle`) and bucket name from `S3fsCred`. Header functions allocate/finalize memory in libcurl-compatible lists that callers must free with `curl_slist_free_all`.

Dependencies/integration: used heavily by `curl.cpp` signing and request setup. Depends on libcurl slist structures, `s3fs_auth` for MD5, `S3fsCred` for bucket, `string_util` for trim/lower/url encode/peeloff helpers, and logger macros. Also declares integration points implemented elsewhere (`get_object_sse_type`, `put_headers`) in the header.

Risks: `curl_slist_sort_insert` builds `strnew` from the original `key` expression rather than the trimmed `strkey`, so leading/trailing spaces in key arguments could be retained in the stored header while sorting uses the trimmed key. Manual allocation must exactly match libcurl's free behavior; replacement frees `data` correctly, but callers must not mix with ownership outside libcurl conventions. `prepare_url` assumes the bucket token exists in `url_str`; malformed input could produce surprising substr ranges. `url_to_host` aborts the process for invalid schemes, which is harsh for configuration errors.

Test signals: unit tests should cover sorted insertion/replacement/removal, empty-header omission in signed header lists, V2 `only_amz` canonicalization, host/path style URL rewrites with service paths and encoded object names, invalid URL scheme behavior, MD5 base64 from binary data, quoted/unquoted ETag comparison, and compatibility with `curl_slist_free_all`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/curl_util.cpp -->
