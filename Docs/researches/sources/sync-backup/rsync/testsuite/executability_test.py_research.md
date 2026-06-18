## sources/sync-backup/rsync/testsuite/executability_test.py

Purpose: validates `--executability`/`-E`, where rsync propagates only executable bits from source to destination while leaving other permission bits alone.

Important APIs and control flow: creates two shell files, attempts a sticky/setuid-style mode on file `1`, skips only on expected permission errors, and runs a baseline `rsync -rvv`. It verifies initial destination modes, then changes source and destination permissions. A second normal rsync run must leave destination permissions unchanged. A final `-rvvE` run must remove execute bits from `1` and add execute bits to `2` while preserving non-execute bits as documented.

State and dependencies: uses `FROMDIR`, `TODIR`, `os.chmod`, `run_rsync`, `check_perms`, and `test_skipped`. Platform behavior around sticky/setuid chmod is explicitly handled.

Integration points: tests receiver permission update logic independent of full `-p` mode preservation.

Risks and test signals: exact permission strings are the primary signal. The setup has portable skip handling for platforms that reject the initial chmod, reducing false failures.
