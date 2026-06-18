<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp18.py -->
# sources/storage-engines/wiredtiger/test/suite/test_timestamp18.py

Purpose: Verifies mixed timestamped and non-timestamped writes, both non-timestamped updates and non-timestamped deletes, over large row and column tables.

Important APIs/types/functions: `test_timestamp18` defines `get_key` to normalize string-row and recno keys. It uses scenario dimensions for key format and non-timestamp operation kind, cursor updates/removes, timestamped commits, `begin_transaction('no_timestamp=true')`, checkpoint, and read-timestamp validation.

Control flow: The test writes 9,999 keys at commit timestamps 2, 3, and 4. It then applies no-timestamp changes to even keys, either deleting them or overwriting with `value4`, checkpoints, and reads at timestamps 2 and 3. Even keys must reflect the non-timestamp operation, while odd keys must retain timestamp-appropriate values.

State and persistence behavior: The test creates dense update chains and then adds globally visible non-timestamp updates. Checkpointing forces reconciliation so the history-store representation is also covered.

Dependencies and integration points: Integrates timestamp visibility, reconciliation, history-store correction for no-timestamp updates, and both row-store and column-store key handling.

Risks: Off-by-one or adjacent-key corruption is explicitly guarded by changing every second key. A bug could allow older timestamped values to appear behind a no-timestamp update or delete.

Test signals: Full-table scans at historical read timestamps validate both coverage of even keys and preservation of odd-key history.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp18.py -->
