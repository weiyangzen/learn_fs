<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/s3api/utils.py -->
# sources/object-store/openstack-swift/swift/common/middleware/s3api/utils.py

## Purpose
Collects small S3 API helpers for sysmeta names, naming conversions, request detection, bucket/key parsing, cipher mapping, S3 timestamp formatting, time parsing, and typed middleware configuration.

## Important APIs, types, and functions
`sysmeta_prefix` and `sysmeta_header` centralize S3 sysmeta header names. `camel_to_snake`, `snake_to_camel`, and `make_header_label` support XML/error/header conversions. `unique_id`, `utf8encode`, and `utf8decode` are encoding helpers. `classify_checksum_header_value` categorizes checksum-looking values. `validate_bucket_name`, `get_s3_access_key_id`, `is_s3_req`, `parse_host`, `parse_path`, and `extract_bucket_and_key` implement S3 request identification and bucket/key extraction. `convert_swift_to_s3_cipher` exposes Swift crypto ciphers as S3 SSE values. `S3Timestamp` adds S3 XML and AWS date formats. `mktime` parses RFC2822/S3 date strings. `Config` supplies default typed config.

## Control flow
Bucket parsing first detects bucket-in-host from configured storage domains, strips host ports, then validates path or host bucket names using DNS-compatible rules when enabled. Invalid URI or bucket names are raised as parse exceptions for callers to translate. `Config.update` and `__setitem__` preserve boolean and integer types based on existing defaults.

## State and persistence behavior
There is no external persistence. `Config` is mutable per middleware/request configuration and defaults include storage domains, region, multipart enablement, no-owner behavior, clock skew, rate-limit error style, and max upload part number. Timestamp helpers convert between Swift timestamps and S3/API wire formats.

## Dependencies and integration points
Used broadly by `s3request`, `s3response`, ACL code, and controllers. It depends on Swift constraints for UTF-8 path validation, Swift `Timestamp`, config parsing, and S3 parse exceptions. Cipher mapping integrates with Swift encryption metadata translated by `s3response`.

## Risks and test signals
Risks include bucket-name compatibility differences when DNS compliance is disabled, host suffix ambiguity for storage domains, weak base64 validation that only decodes without strict size checks, and integer config values silently retaining defaults when set to empty strings. Tests should cover DNS and legacy bucket names, IP-address rejection, invalid UTF-8 paths, virtual-host parsing with ports and multiple storage domains, SigV2/SigV4 access-key extraction, S3 date parsing with timezone offsets, timestamp round trips, and typed `Config` overrides.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/s3api/utils.py -->
