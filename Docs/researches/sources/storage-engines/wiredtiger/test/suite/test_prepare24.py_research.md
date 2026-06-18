# sources/storage-engines/wiredtiger/test/suite/test_prepare24.py

## Purpose

Tests commit of a prepared update after an eviction failure path.

## Important APIs, Control Flow, and State

Using the eviction split failpoint, the test iterates 1000 keys. Each key gets value A at timestamp +10, optional delete at +20, a prepared value B at +30, eviction at the A timestamp with `ignore_prepare=true`, then commit with commit timestamp +30 and durable timestamp +40. It evicts again and verifies timestamp +10 sees A, optional timestamp +20 sees not found, and timestamp +30 sees B.

## Dependencies, Risks, and Test Signals

Dependencies are failpoint eviction, prepared commit, release eviction, and `WT_NOTFOUND`. The risk is failed eviction causing committed prepared updates or prior deletes to lose correct time windows. Signals are repeated read verification after both eviction and commit.
