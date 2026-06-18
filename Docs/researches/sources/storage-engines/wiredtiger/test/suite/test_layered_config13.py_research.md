# sources/storage-engines/wiredtiger/test/suite/test_layered_config13.py

Purpose: tests deletion of local files on restart in disaggregated mode, ensuring layered shared data survives through checkpoint metadata while local non-disaggregated table data is removed.

Important APIs/types/functions: overrides `wiredtiger_open` to ensure log directory exists, patches `helper_disagg.disagg_ignore_expected_output`, uses role reconfigure, `disagg_get_complete_checkpoint_meta`, `close_conn`, `open_conn`, expected stdout `Removing local file`, and checkpoint metadata pickup via reconfigure.

Control flow: the node steps up to leader, creates one layered table and one local table, writes values `aaa`, `bbb`, `ccc` to both across checkpoints, captures checkpoint metadata, closes, then opens without explicit metadata and expects local file removal logging. It reconfigures with captured checkpoint metadata, steps up to leader, verifies layered table value is `ccc`, and asserts opening the local table fails.

State and persistence behavior: shared disaggregated table state persists via checkpoint metadata; local table files/metadata are intentionally discarded under `lose_all_my_data=true` restart behavior. Logging is enabled to exercise local log paths while deleting local data.

Dependencies/integration points: restart cleanup, local file removal, checkpoint metadata pickup, role step-up, and helper output filtering.

Risks: stdout pattern dependency. It tests one key per table but multiple checkpoints.

Test signals: pass means restart cleanup removes local files while checkpoint pickup restores shared layered data.
