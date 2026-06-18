# sources/storage-engines/wiredtiger/test/csuite/wt12015_backup_corruption/main.c

Purpose: this crash harness verifies that incremental backup metadata remains safe when WiredTiger crashes during checkpoint/turtle update or during backup force-stop processing. After the injected crash, it reopens the database, creates another backup using recovered backup IDs, and verifies backup self-consistency.

Important APIs, types, and functions: it uses `WT_CONNECTION`, `WT_SESSION`, backup helpers `testutil_backup_create_full`, `testutil_backup_create_incremental`, `testutil_backup_force_stop`, backup query cursor `"backup:query_id"`, failpoint reconfiguration `debug=(checkpoint_fail_before_turtle_update=true)`, process `fork`, `waitpid`, and signal handling. Main helpers are `populate_table`, `verify_backup`, `do_work_before_failure`, `do_work_after_failure`, `run_test_backup`, and `run_test_force_stop`.

Control flow: `main` parses options, chooses logged or no-log environment config, creates a work home, installs a SIGCHLD handler, and runs scenario 1, scenario 2, or both. In each scenario a child creates the database, table, several full/incremental backups and checkpoints, enables the checkpoint failpoint, creates `expect_abort`, and then calls either checkpoint or backup force-stop expecting the process to abort. The parent waits for the crash, copies the database for debugging, reopens, queries available backup IDs, populates more data, creates a new full or incremental backup, closes, and verifies that backup.

State and persistence behavior: the test persists `backup.N` directories, a `check` directory for verification copies, a `save` copy of the crashed database, and an `expect_abort` sentinel used to suppress expected abort messages. Table data encodes key/value self-consistency by storing `k` in the key suffix and bitwise complement in the value. Verification opens a copied backup and checks every row satisfies `k == ~v`.

Dependencies and integration points: it depends on WiredTiger backup ID metadata, turtle-file update ordering, logging or no-logging environment variants, and test utility backup helpers. It integrates with process-level crash testing and event-handler filtering for expected panic/abort text.

Risks and test signals: critical risks are selecting the wrong recovered backup source ID after a crash, leaving incomplete backup metadata visible, or producing a corrupt incremental backup. Passing requires child death at the expected failpoint, successful reopen, successful follow-on backup, and complete self-consistency verification.
