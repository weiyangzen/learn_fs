# sources/sync-backup/rsync/testsuite/chmod_test.py

Purpose: verifies transfer of varied read-only and special permission bits across whole-file and delta updates.

Important APIs/types/functions: `hands_setup`, `_try_chmods`, `os.chmod`, and two `checkit` calls for normal and `-I --no-whole-file` transfers.

Control flow: set modes on representative files in the hands tree, with fallbacks when special bits are refused. First sync normally, then force a delta update of all files.

State and persistence behavior: source file modes include read-only and setuid/setgid/sticky attempts; destination must preserve them through both transfer paths.

Dependencies and integration points: platform chmod permissions, rsync archive mode preservation, and harness tree comparison.

Risks and test signals: special bits may be downgraded by fallback setup. Failures indicate mode loss during initial copy or delta update.
