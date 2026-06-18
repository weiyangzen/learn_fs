<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_sweep01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_sweep01.py

Purpose: verifies the sweep server closes and removes inactive data handles/files even while checkpoints keep one active table busy.

Important APIs/types/functions: `test_sweep01` uses `suite_subprocess`, `make_scenarios` for row/VLCS tables, `stat.conn` sweep/file stats, `session.checkpoint`, sleeps, and connection config `file_manager=(close_handle_minimum=0,close_idle_time=3,close_scan_interval=1)`.

Control flow: create 30 tables with 1000 records each, capture baseline sweep/file-open stats, create one active table, then loop up to 60 seconds doing checkpoints and inserts on the active table while polling `file_open` and sweep removal stats. Finally compare baseline and final counters.

State and persistence behavior: many table handles become inactive after cursor close. Checkpoints and active writes keep the connection busy while the background sweep server must close dead handles and reduce open files to the expected core set.

Dependencies/integration points: covers file manager sweep, session handle sweeping, checkpoint interaction, file-open accounting, row/VLCS formats, and hook skips for disagg/tiered. Risks include timing sensitivity and expected final file count; signals are increased close/remove/sweep counters and reduced open file count equal to five.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_sweep01.py -->
