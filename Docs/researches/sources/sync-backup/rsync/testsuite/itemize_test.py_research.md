## sources/sync-backup/rsync/testsuite/itemize_test.py

Purpose: detailed regression suite for itemized output (`-i`, `-ii`) and verbose output across normal, hard-link, symlink, checksum, copy/link/compare-dest, dry-run, and delta cases.

Important APIs and control flow: builds a small tree with files from source fixtures, a symlink, and a hard link. It probes `rsync -VV` for `hardlink_symlinks` and `symtimes`, adjusts expected output tokens, then runs many `checkdiff()` calls with exact expected stdout. Between phases it retouches directories, modifies modes/content, replaces symlinks, and creates/removes `to2dir`.

State and dependencies: uses `FROMDIR`, `TODIR`, `to2dir`, source fixture files, itemize constants, `v_filt`, and build-feature detection.

Integration points: exercises itemize formatting for file, dir, symlink, hard-link, basis-dir, compare-dest, link-dest, and copy-dest decisions.

Risks and test signals: exact output comparisons are high-signal but brittle to intentional format changes or feature variation. Feature probes reduce portability risk.
