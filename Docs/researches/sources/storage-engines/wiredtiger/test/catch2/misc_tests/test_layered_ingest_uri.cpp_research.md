# sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_layered_ingest_uri.cpp

## Purpose
Tests deriving a layered table URI from an ingest constituent file URI.

## Important APIs, Types, And Functions
Calls `__ut_layered_derive_layered_uri(WT_SESSION_IMPL *, const char *, WT_ITEM *)` with a mock session and output buffer.

## Control Flow
Valid sections pass `file:<name>.wt_ingest` and assert output `layered:<name>`. Invalid sections check missing `file:` prefix, missing `.wt_ingest` suffix, wrong prefix, and stable suffix.

## State And Persistence Behavior
The function writes derived URI bytes into a `WT_ITEM` buffer that is freed with `__wt_buf_free`. No persistence.

## Dependencies And Integration Points
Depends on `mock_session`, `wt_internal.h`, and layered table naming conventions.

## Risks And Edge Cases
Guards against accepting malformed source URIs or deriving from stable constituent files. Names with underscores and digits are accepted.

## Test Signals
Valid inputs return zero and exact output strings; invalid inputs return `EINVAL`.
