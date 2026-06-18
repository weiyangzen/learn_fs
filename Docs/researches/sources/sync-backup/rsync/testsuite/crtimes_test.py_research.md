# sources/sync-backup/rsync/testsuite/crtimes_test.py

Purpose: verifies create-time preservation when rsync advertises crtimes support.

Important APIs/types/functions: `run_rsync('-VV')`, `_utime`, `rsyncfns.TLS_ARGS = '--crtimes'`, and `checkit(['-rtgvvv', '--crtimes', ...])`.

Control flow: skip without crtimes support. Create a directory and file, touch each first to an old time and then to a newer time to leave create time pinned on supporting systems, enable crtime-aware listing, and sync with `--crtimes`.

State and persistence behavior: source birth/create times are expected to be preserved and visible through the test listing.

Dependencies and integration points: filesystem/kernel create-time behavior, rsync crtimes support, and harness listing.

Risks and test signals: platform semantics for birth time can vary. Failure means crtime metadata was lost or listing comparison disagreed.
