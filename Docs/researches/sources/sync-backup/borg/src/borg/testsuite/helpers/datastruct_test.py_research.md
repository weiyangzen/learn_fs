# sources/sync-backup/borg/src/borg/testsuite/helpers/datastruct_test.py

Purpose: tests deterministic dictionary ordering and reusable buffer sizing.

Important APIs and control flow: `test_stable_dict` verifies `StableDict` sorts items by key and produces a stable msgpack MD5 digest. `TestBuffer` checks backing type creation, initial lengths, grow/shrink behavior, `init=True` forcing reallocation, memory limit enforcement, and `get(size)` reusing or resizing as needed.

State and persistence: in-memory structures only. `Buffer` preserves and reuses internal allocated capacity until explicit reinitialization or growth.

Dependencies and integration points: depends on `StableDict`, `Buffer`, `helpers.msgpack`, and hashlib. Stable serialization affects archive metadata and cache hashes; `Buffer` supports performance-sensitive binary processing.

Risks: stable digest fixtures can break on msgpack configuration changes. `Buffer` allows retained larger allocations after shrink requests, which is intentional but relevant for memory-sensitive callers.

Test signals: exact item ordering, known MD5, allocation identity checks, and `MemoryLimitExceeded`.
