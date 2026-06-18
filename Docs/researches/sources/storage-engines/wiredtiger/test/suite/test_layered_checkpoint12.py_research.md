# sources/storage-engines/wiredtiger/test/suite/test_layered_checkpoint12.py

Purpose: verifies startup database-size verification is deferred until a follower actually picks up checkpoint metadata.

Important APIs/types/functions: `conn_config` enables verbose verify and leader role. `_follower_config` builds `verify_metadata=true` follower configs with optional `checkpoint_meta`. The test uses `disagg_get_complete_checkpoint_meta`, role reconfiguration, `close_conn`, `open_conn`, `reopen_conn`, stdout regex guards, and `ignoreStdoutPattern`.

Control flow: the leader creates data, checkpoints, and captures checkpoint metadata. It steps down before close to avoid a shutdown checkpoint, then opens as follower without checkpoint metadata under a custom stdout assertion that database-size verification does not report checkpoint-size comparison. It then reopens as follower with checkpoint metadata and expects a verify log indicating the checkpoint-size branch ran. Teardown verify verbosity is ignored.

State and persistence behavior: shared checkpoint metadata exists, but follower startup without metadata must not populate enough state to compare database size. Supplying metadata should trigger pickup and then run the comparison.

Dependencies/integration points: startup open path, follower checkpoint pickup, `verify_metadata=true`, verbose verify logging, and disaggregated database-size verification.

Risks: the test is log-pattern sensitive. It validates branch execution by stdout, not by a direct API counter.

Test signals: pass means startup verify avoids false positives on no-pickup follower opens and activates once checkpoint metadata is supplied.
