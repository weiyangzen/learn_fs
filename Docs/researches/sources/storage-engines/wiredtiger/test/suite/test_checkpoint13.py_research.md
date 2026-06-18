# sources/storage-engines/wiredtiger/test/suite/test_checkpoint13.py

Purpose: tests checkpoint cursor API restrictions and timestamp bounds for named and unnamed checkpoints.

Important APIs/types/functions: `SimpleDataSet`, `make_scenarios`, checkpoint `name`, checkpoint cursor `checkpoint_read_timestamp`, `wiredtiger.WT_NOTFOUND`, and error assertions for `/before the checkpoint oldest/` and `/cannot be dropped/`.

Control flow: set oldest/stable to 10, write values at timestamp 20, set stable 20 and create named or unnamed checkpoint, write timestamp-30 values, open checkpoint cursor and verify it reads timestamp-20 data both outside and inside an ordinary transaction, then open at read timestamp 10 and see no data, and assert opening at timestamp 5 fails. For named checkpoints, keep a cursor open and assert regenerating or dropping that checkpoint fails.

State/persistence behavior: checkpoint snapshots carry oldest timestamp bounds and remain immutable while later updates occur. Named checkpoint metadata must be pinned by open cursors.

Dependencies/integration: checkpoint timestamp metadata, cursor transaction handling, named checkpoint lifecycle, precise/fuzzy modes, and hook skips.

Risks/test signals: comments mention older restrictions; current expected behavior allows reads inside a normal transaction but not before checkpoint oldest.
