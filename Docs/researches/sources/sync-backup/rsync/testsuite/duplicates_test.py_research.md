## sources/sync-backup/rsync/testsuite/duplicates_test.py

Purpose: regression coverage for duplicate source arguments. It ensures `clean_flist()` deduplicates repeated directory inputs so each file and symlink transfers exactly once.

Important APIs and control flow: creates `FROMDIR/name1` and a symlink `name2` to it. It invokes rsync manually through `subprocess.run(rsync_argv('-avv', *sources, f'{TODIR}/'))` with the same source directory repeated ten times. It counts verbose output lines for `name1` and `name2 -> ...`, requiring each to appear once, then compares recursive listings with `rsync_ls_lR`.

State and dependencies: uses symlink-capable filesystem state in `FROMDIR` and `TODIR`, and captures stdout to inspect copy behavior.

Integration points: ties directly to sender file-list normalization, duplicate source handling, symlink output, and listing verification through `tls`.

Risks and test signals: symlink creation may fail on restricted platforms and becomes a hard failure. The strongest signal is output cardinality, which catches duplicate-transfer regressions that final tree equality alone would miss.
