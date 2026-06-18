# sources/object-store/rustfs/crates/ecstore/src/bucket/object_lock/objectlock.rs

Purpose: Parses per-object object-lock metadata headers into S3 DTO retention and legal-hold values. It also exposes a time source helper and constants for object-lock error text.

Important APIs and types: `utc_now_ntp` returns current UTC time. `get_object_retention_meta` reads `x-amz-object-lock-mode` and `x-amz-object-lock-retain-until-date` from user metadata, parses mode and ISO8601 date, and returns `ObjectLockRetention`. `get_object_legalhold_meta` parses `x-amz-object-lock-legal-hold`. `parse_ret_mode` accepts GOVERNANCE and COMPLIANCE case-insensitively. `parse_legalhold_status` accepts ON and OFF case-insensitively.

Control flow and state: All functions are stateless and intentionally non-panicking for malformed metadata. Invalid modes or legal-hold values return DTOs with `None` status/mode. Date parse failures simply omit `retain_until_date`.

Dependencies and integration: Uses `s3s::dto` object-lock types, S3 header constants, `HashMap<String, String>` user metadata, and `time` ISO8601 parsing. `objectlock_sys.rs` builds deletion/modification decisions on these parsed DTOs.

Risks: Header lookup assumes metadata keys are lower-case exactly as `s3s::header` constants. Invalid or unparsable retention date becomes absent rather than an error, so callers must decide whether to reject invalid user input earlier. Error constants are currently unused.

Test signals: Unit tests cover valid/invalid mode parsing, valid/invalid legal hold parsing, empty metadata, retention with mode/date, and invalid value behavior.
