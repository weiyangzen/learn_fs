# sources/distributed-fs/tahoe-lafs/src/allmydata/immutable/downloader/common.py

## Purpose
Defines shared downloader state labels and exception types used across segment fetching, share fetching, node orchestration, and segmentation.

## Important APIs, Types, And Functions
State constants are `AVAILABLE`, `PENDING`, `OVERDUE`, `COMPLETE`, `CORRUPT`, `DEAD`, and `BADSEGNUM`. Exceptions are `BadSegmentNumberError`, `WrongSegmentError`, and `BadCiphertextHashError`.

## Control Flow
No active control flow. Constants are compared by identity or equality by caller modules to route share/block events.

## State And Persistence
No mutable state or persistence.

## Dependencies And Integration Points
Imported by `fetcher.py`, `segmentation.py`, and `node.py`. `Share.get_block()` emits terminal/nonterminal states consumed by `SegmentFetcher._block_request_activity`; segmentation uses the segment-number and wrong-segment exceptions for retry behavior; `DownloadNode._check_ciphertext_hash()` raises `BadCiphertextHashError`.

## Risks And Edge Cases
The states are plain strings, not an enum, so typo safety is limited. Some code imports only subsets, making additions require careful search across downloader modules and tests.

## Test Signals
`src/allmydata/test/test_download.py` imports these exceptions directly and exercises bad segment, wrong segment retry, corrupt block, and ciphertext hash failure paths.
