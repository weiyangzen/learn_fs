# sources/sync-backup/rsync/testsuite/alt-dest_test.py

Purpose: broad functional coverage of local and remote-shell alternative-destination options, including stacked `--compare-dest`/`--copy-dest` and `copy_file()` tmpfile paths.

Important APIs/types/functions: `hands_setup`, `run_rsync`, `checkit`, `rmtree`, `test_fail`, `RSYNC_PEER`, support `lsh.sh`, and inode checks with `os.stat`.

Control flow: seed `alt1` and `alt2` with selected subtrees of `FROMDIR`, create `alt3/likely` as a same-name candidate, update source mtimes, build `CHKDIR`, then run stacked compare-dest and copy-dest checks. It then loops over normal and `--inplace` copy-dest transfers, locally and through lsh remote-source/remote-dest variants, verifying destination equality and that `--copy-dest` copies rather than hardlinks the candidate.

State and persistence behavior: maintains several alternate basis directories, destination resets, and source timestamp changes to force comparison logic. Destination content must match source while selected alt-dest files are excluded or copied as expected.

Dependencies and integration points: rsync local transfer, remote-shell stand-in, alternate-dest receiver logic, tmpfile copy path, and harness directory comparison.

Risks and test signals: failures identify stacked basis lookup errors, copy-vs-link semantic regressions, or protocol/remote-shell argument handling issues.
