## sources/sync-backup/rsync/testsuite/hands_test.py

Purpose: canonical end-to-end transfer smoke test over a rich fixture produced by `hands_setup()`.

Important APIs and control flow: performs six phases: basic `-av`; hard-link preservation after linking `filelist` into a subdir with `-H`; single-file repair after deleting destination `text`; delta repair after appending extra data and using `--no-whole-file`; `--delete` cleanup of a stray destination file; and non-recursive globbed copy of top-level entries followed by an exclude-all comparison pass.

State and dependencies: mutates the standard `from`/`to` trees, creates hard links, appends files, changes cwd to `TMPDIR`, and uses `checkit` plus direct `run_rsync`.

Integration points: broad integration coverage for archive transfer, hard links, delta algorithm, delete behavior, and argument expansion.

Risks and test signals: primarily final directory and file diffs from `checkit` after each phase. It is broad but less diagnostic than focused tests.
