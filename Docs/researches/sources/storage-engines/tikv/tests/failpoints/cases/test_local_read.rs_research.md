# sources/storage-engines/tikv/tests/failpoints/cases/test_local_read.rs

## Purpose
This file verifies local-reader consistency when a lease-read request has already passed lease validation but the peer is then removed and its local range is cleaned before the async response is returned.

## Important APIs, Types, and Functions
- `test_consistency_after_lease_pass` uses raw KV requests through `TikvClient`.
- `localreader_before_redirect` proves the request is served by local reader.
- `after_pass_lease_check` pauses after lease validation, and `apply_snap_cleanup_range` pauses snapshot cleanup.
- `must_raw_put`, `must_raw_get`, `must_get_equal`, `must_get_none`, and PD peer add/remove helpers are the core harness calls.

## Control Flow
The test starts a three-store cluster, transfers leadership to store 1, writes `key1`, and verifies a local lease read. It then pauses immediately after lease check and sends an async raw-get. While the request is paused, it transfers leadership away, removes the old peer, adds a replacement peer with snapshot cleanup paused, waits until old data is deleted locally, resumes the read, and asserts the paused request still returns the original value.

## State and Persistence Behavior
The important state is the snapshot acquired after passing lease validation. Even if the range is later cleaned from the engine due to peer removal and replacement snapshot application, the read must remain backed by the already-acquired snapshot and return consistent data.

## Dependencies and Integration Points
The test spans local reader lease validation, raw KV RPC, PD conf change, peer removal, snapshot application cleanup, and raftstore storage snapshots.

## Risks and Test Signals
The risk is a time-of-check/time-of-use bug where local reader validates lease before snapshot acquisition or lets cleanup invalidate the read. Signals are `must_get_none` after cleanup and the async raw-get returning `value1` after resume.
