# sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_disagg_meta_config.cpp

## Purpose
Tests parsing of disaggregated storage checkpoint metadata, crypt key metadata, legacy metadata format, and metadata version/compatible-version handling.

## Important APIs, Types, And Functions
`disagg_fixture` holds sample `checkpoint`, `timestamp`, and `key_provider` config fragments and a mock session. Tests call `__wt_disagg_parse_meta`, `__wti_disagg_parse_crypt_meta`, and `__ut_disagg_parse_version_and_check`.

## Control Flow
Metadata parsing sections cover all fields, missing optional key provider, missing required fields, null/empty metadata, truncated length, unknown keys under future version, and unknown keys under matching version. Crypt metadata sections cover well-formed page ID/LSN extraction and malformed values/missing fields/unsupported version. Legacy sections parse newline-separated checkpoint+timestamp metadata and invalid timestamp cases. Version sections check valid, incompatible, missing version, missing compatible version, and default version when omitted.

## State And Persistence Behavior
All parsed fields in `WT_DISAGG_METADATA` are views into the input buffer with lengths, not durable copies. Timestamp strings are parsed from hex. No disk state is written.

## Dependencies And Integration Points
Depends on `wt_internal.h`, `mock_session`, `utils.h`, string streams/views, and disaggregated checkpoint turtle constants.

## Risks And Edge Cases
Risks include accepting malformed crypt metadata, reading past provided buffer length, mishandling unknown keys for future metadata, rejecting legacy metadata, and accepting incompatible versions.

## Test Signals
Return codes (`0`, `EINVAL`, `ENOTSUP`), exact string views, parsed timestamps, page IDs, LSNs, and default version fields are asserted.
