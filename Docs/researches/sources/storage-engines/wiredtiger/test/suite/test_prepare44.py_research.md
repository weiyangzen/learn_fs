# sources/storage-engines/wiredtiger/test/suite/test_prepare44.py

## Purpose

Regression test for an in-memory page eviction assertion involving an aborted prepared update at the tail of an update chain.

## Important APIs, Control Flow, and State

The test is skipped for tiered storage and uses `precise_checkpoint=true,preserve_prepared=true` with an in-memory, non-logged table. It prepares key 1, rolls it back at timestamp 15, then commits a new value for key 1 at timestamp 20 and adds many more keys to fill the page. Oldest is not advanced past committed updates so they are not globally visible. A release-evict cursor with `ignore_prepare=true` searches key 1, expects the committed value, and resets to evict. A timestamp-20 read verifies the committed value remains.

## Dependencies, Risks, and Test Signals

Dependencies are in-memory storage, prepared IDs, debug eviction, and timestamp reads. The risk is aborted prepared tail state setting `has_newer_updates` and tripping in-memory split assertions. Signals are no crash during eviction and correct post-eviction readback.
