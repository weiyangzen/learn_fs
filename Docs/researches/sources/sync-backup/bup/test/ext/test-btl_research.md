## sources/sync-backup/bup/test/ext/test-btl

Purpose: validates helper functions from `test/lib/btl.sh` for redirecting stdout/stderr and preserving exit codes.

Important control flow: defines `out-err()` that writes to both streams, then checks `err-to`, `out-to`, and `both-to` capture the correct stream content. A second group verifies those wrappers preserve success, failure, and an explicit exit status 42.

State and dependencies: creates temporary log files under a temp directory. Depends on `wvtest-bup.sh` and `btl.sh`.

Risks and integration: these helpers are used by many later shell tests to assert stderr/stdout content, so this test protects the reliability of the test suite itself.
