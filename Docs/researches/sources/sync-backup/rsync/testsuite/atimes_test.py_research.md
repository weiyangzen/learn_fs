# sources/sync-backup/rsync/testsuite/atimes_test.py

Purpose: verifies access-time preservation when rsync advertises atime support.

Important APIs/types/functions: `run_rsync('-VV')`, `rsyncfns.TLS_ARGS = '--atimes'`, `os.utime`, and `checkit(['-rtUgvvv', ...])`.

Control flow: skip without atime support. Create `FROMDIR/foo`, set its atime to a fixed 2001 timestamp while retaining mtime, enable atime-aware test listing, then sync with `-U` and compare source/destination listings.

State and persistence behavior: source atime is explicit metadata; destination atime should be persisted by rsync and visible through the harness listing.

Dependencies and integration points: filesystem atime support, rsync `-U`/`--atimes`, and `rsyncfns` listing configuration.

Risks and test signals: filesystems mounted with unusual atime behavior can make this fragile. Failure means atime metadata is not preserved or not reflected in the listing.
