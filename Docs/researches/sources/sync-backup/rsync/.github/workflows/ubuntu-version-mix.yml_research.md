# sources/sync-backup/rsync/.github/workflows/ubuntu-version-mix.yml

Purpose: compatibility tests between current rsync and bundled older rsync binaries.

Important APIs/types/functions: builds current `check-progs`, then loops over `old_versions/rsync_*`, matching each to a `testsuite/expect/<name>.expect` file, and runs `runtests.py` with `--rsync-bin2` for both pipe and TCP transports.

Control flow: scheduled weekly at a distinct minute and path-filtered triggers. Failures accumulate in `rc` so all peer/transport combinations run before final exit.

State and persistence: no artifact on success; logs grouped per peer/transport.

Dependencies/integration: depends on old binary executability and expectation files.

Risks: old binaries may be incompatible with new runner libraries; expectation files must track intended differences.

Test signals: matrix of current-vs-old compatibility across transports.
