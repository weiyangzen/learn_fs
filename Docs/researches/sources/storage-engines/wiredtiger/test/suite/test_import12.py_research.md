# sources/storage-engines/wiredtiger/test/suite/test_import12.py

Purpose: stresses repeated import/drop/reimport of a file after checkpoints and alters, including fallback to `repair=true` when a second metadata import encounters checkpoint/root-page problems.

Important APIs and functions: inherits `test_import_base`; uses `WiredTigerError`, `wiredtiger_strerror`, and `WT_ERROR` to normalize expected repairable failures. Class attributes define original/new file names, two `access_pattern_hint` alter configs, and `max_ckpt=2`.

Control flow: the test creates the original file, writes/checkpoints two batches, exports metadata, closes, then loops over checkpoint counts 0-2. For each loop it recreates `IMPORT_DB`, imports the copied file under a new URI, checkpoints one or more times, alternates an `alter` setting, checkpoints, confirms latest metadata contains the alter, drops the table with `remove_files=false`, tries a second metadata import with `panic_corrupt=false`, falls back to `repair=true` if WT_ERROR occurs, verifies, checks values, appends rows, and closes the connection.

State and persistence behavior: the first import/drop leaves a file with multiple checkpoints and altered metadata. The second import tests whether import selects a valid/latest checkpoint; repair import is expected to recover when normal import cannot.

Dependencies and integration points: integrates import, alter, checkpoint force mode, drop without remove, repair import, metadata inspection, verification, and stderr/stdout ignore hooks.

Risks and edge cases: comments reference known issues WT-13639 and WT-14713. Some repair metadata assertions are commented out, so the test currently validates usability more than exact metadata preservation after fallback.

Test signals: latest metadata includes the alter before drop; second import or repair succeeds; verification and data checks pass across all checkpoint-loop variants.
