# sources/storage-engines/wiredtiger/test/suite/test_util15.py

## Purpose

`test_util15.py` verifies the `wt alter` utility updates table metadata by changing `access_pattern_hint` from sequential to random.

## Important APIs, Types, and Functions

The single `test_alter_process` method creates a table, invokes `wt alter`, opens the `metadata:create` cursor, searches for the table metadata key, and checks the returned config string.

## Control Flow

The test performs two alter cycles. After each `runWt(["alter", uri, config])`, it reads metadata directly and asserts the new access-pattern setting appears in the stored create config.

## State and Persistence Behavior

The persistent state is table metadata in WiredTiger's metadata file; no table data is required. Metadata changes survive the subprocess boundary.

## Dependencies and Integration Points

Integrates the `wt alter` command, metadata cursor access, table existence helper, and string config representation.

## Risks and Edge Cases

The assertion is substring-based, so it does not detect duplicate conflicting settings. It covers only one alterable setting and does not test invalid configs or active cursors.

## Test Signals

Expected signals are successful utility exit and metadata containing `access_pattern_hint=sequential` and later `access_pattern_hint=random`.
