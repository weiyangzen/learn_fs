## sources/sync-backup/rsync/testsuite/fuzzy_test.py

Purpose: canonical `--fuzzy` regression test using an existing destination file under a different name as the delta basis, while `--delete-delay` removes the stale basis later.

Important APIs and control flow: copies `rsync.c` to `FROMDIR/rsync.c`, copies it with preserved times to `TODIR/rsync2.c`, sleeps to avoid timestamp ambiguity, and runs `rsync -avvi --no-whole-file --fuzzy --delete-delay --debug=FUZZY`. It asserts debug output says `rsync2.c` was selected as the basis, then calls `verify_dirs(FROMDIR, TODIR)`.

State and dependencies: depends on `SRCDIR/rsync.c`, `cp_p`, `cp_touch`, timing, and `verify_dirs`.

Integration points: covers generator fuzzy matching, delta update path, delayed delete cleanup, and final tree equality.

Risks and test signals: debug output is required to prove fuzzy engaged. Final tree equality verifies delete-delay removed the old basis.
