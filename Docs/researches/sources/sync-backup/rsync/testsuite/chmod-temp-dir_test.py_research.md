# sources/sync-backup/rsync/testsuite/chmod-temp-dir_test.py

Purpose: mirrors chmod transfer coverage while routing temp files through a different filesystem to force cross-filesystem rename fallback.

Important APIs/types/functions: `_fsdev`, `TOOLDIR/getfsdev`, `hands_setup`, `_try_chmods`, `checkit`, and `test_skipped`.

Control flow: prepare standard hands tree, find a writable temp directory on a different device than `SCRATCHDIR`, set varied file modes, run a normal copy with `--temp-dir`, then run an update with `-I --no-whole-file --temp-dir`.

State and persistence behavior: source mode metadata and destination content/modes are verified after temp-file copy/unlink fallback rather than same-filesystem rename.

Dependencies and integration points: `getfsdev` test tool, availability of another writable filesystem, rsync temp-dir code, and chmod preservation.

Risks and test signals: skips if no separate filesystem is available. Failures identify metadata/content loss in cross-device temp-file handling.
