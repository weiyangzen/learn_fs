## sources/sync-backup/rsync/testsuite/open-noatime_test.py

Purpose: verifies `--open-noatime` leaves the source access time unchanged during transfer of a non-empty file.

Important APIs and control flow: probes `rsync -VV` for atime support and skips non-Linux platforms because `O_NOATIME` is Linux-specific. It creates `FROMDIR/foo`, pins its atime to a fixed historical timestamp, sets `rsyncfns.TLS_ARGS = '--atimes'`, captures a `tls` listing before transfer, runs rsync with `--open-noatime --archive --recursive --times --atimes -vvv`, captures a second listing, and diffs on mismatch.

State and dependencies: mutates `TLS_ARGS`, writes `TMPDIR/atime-from-before` and `atime-from-after`, depends on `TOOLDIR/tls`.

Integration points: covers source file opening flags and atime preservation through rsync's archive/atime paths.

Risks and test signals: avoids `checkit` because diffing source files would change atime. Exact `tls` listing equality is the signal.
