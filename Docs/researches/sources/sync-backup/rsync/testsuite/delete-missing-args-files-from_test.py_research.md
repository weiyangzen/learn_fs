# sources/sync-backup/rsync/testsuite/delete-missing-args-files-from_test.py

Purpose: functional regression for `--delete-missing-args` with `--files-from` over daemon upload, covering missing file and directory entries.

Important APIs/types/functions: `write_daemon_conf`, `start_test_daemon`, `rsync_argv('-a', '--delete', '--delete-missing-args', '--files-from=...')`, `test_xfail`, and final filesystem assertions.

Control flow: create daemon module containing stale `keep.txt`, missing-on-sender `ghost.txt`, and `ghostdir`; create sender with only `keep.txt`; write files-from list containing all three names. Upload to daemon. If output shows known `invalid file mode 00`/protocol code 2 symptom while ghosts remain, mark xfail. Otherwise require success, ghosts deleted, and keep updated.

State and persistence behavior: module destination state is the oracle: missing args should be deleted and present file updated.

Dependencies and integration points: flist mode-0 missing entry handling, daemon receiver/generator delete logic, files-from, and xfail harness.

Risks and test signals: currently may xfail on affected versions. Unexpected failures after known symptom is absent indicate a different regression.
