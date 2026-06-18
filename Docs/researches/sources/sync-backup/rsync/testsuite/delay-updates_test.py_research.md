# sources/sync-backup/rsync/testsuite/delay-updates_test.py

Purpose: basic `--delay-updates` regression covering stale root staging file overwrite.

Important APIs/types/functions: `checkit`, `os.utime`, `FROMDIR`, `TODIR`.

Control flow: create source `foo=1`, sync with `--delay-updates`, then create `TODIR/.~tmp~/foo=2`, touch staged and visible files to a reference time, change source to `3`, and sync again. Both transfers compare destination to source.

State and persistence behavior: root-level `.~tmp~` staging content is deliberately stale and should not survive or corrupt the final file.

Dependencies and integration points: delayed-update receiver logic and harness directory comparison.

Risks and test signals: failure means stale staging content won or destination did not match source.
