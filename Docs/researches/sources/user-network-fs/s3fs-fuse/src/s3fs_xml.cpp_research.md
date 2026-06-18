# sources/user-network-fs/s3fs-fuse/src/s3fs_xml.cpp

Purpose: implements XML parsing helpers for S3 ListBucket/ListObjects responses, continuation markers, incomplete multipart upload listings, object extraction into `S3ObjList`, and simple single-key XML extraction.

Important APIs and functions: `GetXmlNsUrl` caches namespace discovery. `get_base_exp`, `get_prefix`, `get_next_continuation_token`, `get_next_marker`, and `is_truncated` extract common response fields. `get_object_name` reduces full S3 keys relative to a listed path. `get_incomp_mpu_list` builds incomplete multipart upload records. `append_objects_from_xml_ex` and `append_objects_from_xml` populate `S3ObjList` from `Contents` and `CommonPrefixes`. `simple_parse_xml` parses a small document and returns the text for a named child element.

Control flow: callers pass a parsed libxml document. Namespace-aware XPath expressions are assembled dynamically unless `noxmlns` is set. Object appending discovers the response prefix, creates XPath contexts, appends contents and common prefixes separately, extracts optional ETag/Size/LastModified, decodes encoded CR characters, and inserts normalized names into `S3ObjList`.

State and persistence: static namespace cache stores one namespace string for up to 60 seconds under `xml_parser_mutex`; this is process-wide, not document-specific. Parsed results are stored in caller-owned `S3ObjList` or incomplete MPU lists. No disk persistence.

Dependencies and integration points: uses libxml2 XPath/parser APIs, global `noxmlns`, logging, path helpers from `s3fs_util`, string conversions from `string_util`, MPU types, and `S3ObjList`.

Risks: namespace caching is global and time-based, so mixed S3-compatible endpoints with different namespaces in the same process can be parsed with stale namespace data. XPath construction is repetitive and string-based. `get_object_name` path-relative logic is subtle for root, trailing slash, and nested prefix cases. `simple_parse_xml` only checks direct children and is not a general XML query helper. Global `xmlSetGenericErrorFunc` in `s3fsXmlBufferParserError` affects libxml process state.

Test signals: XML fixtures with and without namespaces, ListObjects v1/v2 truncation tokens, root and nested prefixes, common prefixes, CR-encoded keys, ETag/size/last-modified extraction, incomplete MPU lists, malformed XML error buffering, `noxmlns` mode, and mixed namespace documents.
