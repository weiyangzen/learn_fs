# sources/storage-engines/wiredtiger/test/suite/test_layered_checkpoint07.py

Purpose: validates checksum handling in disaggregated checkpoint metadata, including backward-compatible missing-checksum pickup and rejection of corrupted checksum metadata.

Important APIs/types/functions: uses `disagg_get_complete_checkpoint_meta`, regex extraction/replacement, `conn.reconfigure(disaggregated=(checkpoint_meta=...))`, `restart_without_local_files(pickup_checkpoint=False)`, `captureout.checkAdditionalPattern`, and `assertRaisesWithMessage`.

Control flow: the test creates a layered table, writes three values at timestamp 1, sets stable timestamp, checkpoints, and captures the checkpoint metadata string. It asserts `metadata_checksum=` exists, extracts it, steps down to follower, and restarts without auto-pickup. It removes the checksum field from metadata and reconfigures with that metadata, expecting a missing-checksum log but successful data reads. It restarts again, flips checksum bits, reconfigures with corrupted metadata, and expects a `Checkpoint metadata corruption detected` error.

State and persistence behavior: the durable state is the checkpoint metadata string and the data reachable through it. The test intentionally mutates metadata only through reconfigure strings to validate checksum parsing before/while pickup.

Dependencies/integration points: covers checkpoint metadata serialization, follower pickup validation, checksum compatibility policy, and error reporting.

Risks: the missing-checksum branch is explicitly temporary via FIXME-WT-16000; future behavior changes will require test updates. Regex assumptions must track metadata formatting.

Test signals: pass means valid metadata contains checksum, legacy no-checksum metadata still works with warning, and corrupted metadata is rejected before silently loading bad state.
