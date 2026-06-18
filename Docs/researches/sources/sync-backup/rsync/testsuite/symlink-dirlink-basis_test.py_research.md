# sources/sync-backup/rsync/testsuite/symlink-dirlink-basis_test.py

Purpose: regression coverage for updating files through in-tree directory symlinks with `-K/--copy-dirlinks` after secure path resolution changes for CVE-2026-29518. It targets issue #715, where `O_NOFOLLOW` on every component blocked legitimate directory symlinks.

Important APIs and flow: skips unless `resolve_beneath_supported()` proves the binary can securely follow in-tree dir symlinks. It sets `RSYNC_RSH` to `support/lsh.sh`, uses a scratch source base, and defines `push()` to run rsync from that base with `--rsync-path` before positional args. The eight scenarios cover basic dir-symlink initial/update, compressed update, nested symlinks, `--backup`, `--inplace`, top-level file updates, `--partial-dir` with protocol 28, and protocol 28 basic update. `make_testfile()` creates ~32 KiB files to trigger delta matching; `assert_same()` verifies content.

State and persistence: test state lives under `TMPDIR/src_files` and `SCRATCHDIR` home. Several cases unlink previous outputs and modify mtimes with `time.sleep(1)` plus `touch()` to force updates.

Dependencies and integration: exercises receiver secure opening, basis-file handling, remote shell mode, compression, backup, inplace, partial-dir, and legacy protocol behavior. Risks are resolver capability detection and remote-shell setup. Test signal is file existence through the symlink target plus byte identity and backup content correctness.
