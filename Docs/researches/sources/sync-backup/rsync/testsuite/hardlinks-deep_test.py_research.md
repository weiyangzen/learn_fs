## sources/sync-backup/rsync/testsuite/hardlinks-deep_test.py

Purpose: verifies `-H` preserves a hard-link relationship across different nested directories, and that omitting `-H` creates independent files.

Important APIs and control flow: builds `FROMDIR/a/aa/orig` and hard links it to `FROMDIR/b/bb/hardlink`. It runs `rsync -aH` and asserts the destination paths share an inode, then clears `TODIR`, runs `rsync -a`, and asserts they do not.

State and dependencies: uses `os.link`, `makepath`, `rmtree`, `run_rsync`, and hard-link assertion helpers.

Integration points: targets hard-link bookkeeping across directory boundaries, complementing root-level hard-link tests.

Risks and test signals: filesystem hard-link support is assumed; same-inode versus not-same-inode checks are strong behavioral signals.
