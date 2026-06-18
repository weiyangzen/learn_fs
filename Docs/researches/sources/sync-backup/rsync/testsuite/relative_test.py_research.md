## sources/sync-backup/rsync/testsuite/relative_test.py

Purpose: broad `--relative`/`-R` regression test for anchored paths, hard links, delete behavior, and merging extra anchored files.

Important APIs and control flow: creates a deep `FROMDIR/down/3/deep` and temporarily overrides `rsyncfns.FROMDIR` so `hands_setup()` populates that nested directory. It builds an external `extra` tree and a `./`-anchored extra file path. It seeds `CHKDIR`, changes cwd to `FROMDIR`, and runs `checkit()` for basic `-R`, hard-link preservation with `-H`, and `--del`. It manually captures output for no-op delete runs and fails on any `deleting ` line. It then tests merging the deep source with the extra anchored file, with and without `--del`.

State and dependencies: mutates module global `rsyncfns.FROMDIR` temporarily, uses `CHKDIR`, `TODIR`, `OUTFILE`, and cwd changes.

Integration points: file-list anchoring, implied parent paths, hard links under relative mode, and delete scoping.

Risks and test signals: output grep for erroneous deletes catches regressions final tree equality might miss. Global override is restored in `finally`.
