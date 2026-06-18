## sources/sync-backup/rsync/testsuite/link-dest-relative-basis_test.py

Purpose: regression test for issue #915, where daemon receivers ignored relative alt-basis dirs such as `../01`, silently re-transferring files instead of using the basis.

Important APIs and control flow: builds module root `bakmod` with basis `01/f.dat` and source `src915/f.dat`. `push(opt)` creates a fresh dest `00` and runs rsync with `--stats`; `same_inode()` checks hard links; `literal_bytes()` parses stats. It tests three modes: `--link-dest` must hard-link, `--copy-dest` must send little literal data, and `--compare-dest` must skip creating the file. Any regression list is reported as `test_xfail`.

State and dependencies: starts daemon on port 12915, writes daemon config, uses regex parsing and inode checks.

Integration points: exercises shared `check_alt_basis_dirs()` behavior across link/copy/compare-dest in daemon sanitize-path contexts.

Risks and test signals: intentionally XFAILs where safe relative basis climbs are unsupported. Distinct signals per option reduce false positives.
