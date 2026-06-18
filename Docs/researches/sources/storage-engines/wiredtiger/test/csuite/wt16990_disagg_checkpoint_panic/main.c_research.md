# sources/storage-engines/wiredtiger/test/csuite/wt16990_disagg_checkpoint_panic/main.c

Purpose: this process-level regression test verifies that a disaggregated storage checkpoint error during shared metadata queue processing triggers `WT_PANIC`. The panic is required because metadata has already been written and continuing could risk corruption.

Important APIs, types, and functions: it uses disaggregated storage options from `TEST_OPTS`, `block_manager=disagg` table configuration, `WT_CONNECTION::reconfigure` with `timing_stress_for_test=[failpoint_disagg_checkpoint_queue_drain]`, `WT_CONNECTION::set_timestamp`, checkpoints, and a custom error handler. `panic_event_handler` writes errors to stderr and exits cleanly on `WT_PANIC`. `subtest_run` performs the child workload. `main` forks and verifies child status plus stderr contents.

Control flow: `main` parses build/home/preserve/disagg flags, sets `page_log_home`, recreates the home, and forks. The child disables core files, redirects stderr to `stderr.txt`, opens WiredTiger with the panic handler, creates and populates a disaggregated file, sets stable timestamp 10, and checkpoints successfully. It then enables the failpoint, creates/populates a second disaggregated file to ensure shared metadata queue entries exist, sets stable timestamp 20, and checkpoints expecting panic. The parent waits, requires a clean success exit from the panic handler, then scans `stderr.txt` for the expected message fragment.

State and persistence behavior: the test persists disaggregated page-log state in the test home and an stderr capture file. It deliberately does not inspect recovered data; it validates that the failure mode is panic rather than silent continuation.

Dependencies and integration points: it depends on disaggregated storage being enabled through test options, the failpoint name, the panic error path, and the specific diagnostic message "failed while processing shared metadata queue".

Risks and test signals: message text changes can cause false failures even if panic occurs. The child uses `_exit` from the event handler to avoid diagnostic abort handling. Passing requires no child signal, exit success, and the expected panic text in stderr.
