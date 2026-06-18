# sources/sync-backup/rsync/testsuite/chgrp_test.py

Purpose: verifies group preservation with `-g` for every supplementary group available to the test user.

Important APIs/types/functions: `rsync_getgroups`, `os.chown`, fallback `chgrp`, `checkit(['-rtgpvvv', ...])`, and `test_fail`.

Control flow: obtain groups, create one source file per group, set its group via `os.chown` or `chgrp`, wait for timestamp separation, then sync with group preservation and compare listings.

State and persistence behavior: source files carry varied group IDs; destination group metadata must match.

Dependencies and integration points: host group database, permissions to chgrp to member groups, external `chgrp`, and rsync group preservation.

Risks and test signals: fails if no groups or no chgrp tool. Signal is harness listing mismatch for group ownership.
