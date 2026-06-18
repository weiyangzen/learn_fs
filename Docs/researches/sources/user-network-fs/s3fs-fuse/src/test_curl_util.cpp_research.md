# sources/user-network-fs/s3fs-fuse/src/test_curl_util.cpp

## Purpose
Standalone unit test for `curl_util.cpp` list manipulation helpers, especially sorted insertion and removal of libcurl `curl_slist` headers.

## Important APIs, Types, And Control Flow
The file defines a minimal `S3fsCred` stub to satisfy linkage for `curl_util.cpp`. `assert_is_sorted` walks a `curl_slist` and is intended to compare adjacent header keys case-insensitively. `curl_slist_length` counts nodes. `test_sort_insert` inserts keys in head, tail, middle, and replacement positions and checks the head replacement and length. `test_slist_remove` removes absent, sole, head, tail, and middle entries.

## State And Persistence
State is transient in heap-allocated libcurl lists. Each test frees lists with `curl_slist_free_all`; no external state is persisted.

## Dependencies And Integration Points
Depends on `curl_util.h`, libcurl slist types, `test_util.h`, and the link-time stub for `S3fsCred::GetBucket`. It protects HTTP header canonicalization behavior used by signing and request construction.

## Risks And Test Signals
`assert_is_sorted` currently derives both `key1` and `key2` from the same node, so it does not actually compare adjacent nodes; insertion ordering is only partially checked by downstream expectations. Removal coverage is useful but does not assert remaining key order/content after every case. Build and `make check` compile/link behavior are important test signals because the file intentionally avoids linking full credential logic.
