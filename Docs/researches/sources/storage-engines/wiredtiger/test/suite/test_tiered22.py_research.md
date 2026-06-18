# sources/storage-engines/wiredtiger/test/suite/test_tiered22.py

## Purpose
`test_tiered22.py` verifies that compaction is not supported on tiered object files.

## Important APIs, Types, and Functions
The class uses `TieredConfigMixin`, `gen_tiered_storage_sources(..., tiered_only=True)`, `session.create`, `session.compact`, and `assertRaisesWithMessage`.

## Control Flow
The test creates `table:tiered` with string keys and values, asserts that the expected first local tiered object file `tiered-0000000001.wtobj` exists, then calls `session.compact` on that local object file and expects `Operation not supported`.

## State and Persistence Behavior
The test relies on schema creation producing a local tiered object file before data writes. It validates that object files managed by tiered storage are not compacted through the normal file compaction API.

## Dependencies and Integration Points
It integrates with tiered object file naming, schema create side effects, and compaction command validation.

## Risks and Test Signals
The risk is allowing compaction to mutate an object whose lifecycle belongs to tiered storage. The signal is the expected unsupported-operation error after confirming the file exists.
