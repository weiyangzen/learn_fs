## sources/sync-backup/rsync/testsuite/files-from_test.py

Purpose: verifies `--files-from=LIST` for a canonical hands fixture locally and across local remote-shell combinations.

Important APIs and control flow: calls `hands_setup()` to populate `FROMDIR`, writes a `filelist` containing anchored `from/./` entries and selected nested paths, then builds `CHKDIR` by syncing source while excluding entries that should not be present. It first runs a local `checkit`, then loops over four combinations of files-list host and source/destination host using `lsh.sh`, `--rsync-path`, and `-e`.

State and dependencies: uses standard scratch dirs plus `SRCDIR/support/lsh.sh`, `RSYNC_PEER`, and `rmtree` between remote-shell cases.

Integration points: covers files-from path anchoring, remote files-from retrieval, local-to-remote and remote-to-local transfers, and expected tree comparison through `checkit`.

Risks and test signals: remote-shell helper availability and path prefix handling are the main risk. Signal is final `CHKDIR` versus `TODIR` equality for every host placement combination.
