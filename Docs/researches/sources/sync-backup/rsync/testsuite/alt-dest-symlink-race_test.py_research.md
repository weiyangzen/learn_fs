# sources/sync-backup/rsync/testsuite/alt-dest-symlink-race_test.py

Purpose: daemon security regression for basedir confinement in alternate-destination lookup when the basedir parent is a symlink planted inside the module.

Important APIs/types/functions: daemon config writing, `start_test_daemon`, `rsync_argv`, uid/gid helpers, `rmtree`, and inode comparison between module and outside files.

Control flow: create module, outside directory, and source. Plant `module/cd -> outside`; create source `target.txt` matching outside content, mode, and mtime. Start a writable daemon module and push with `--link-dest=cd` into the module root. Fail if destination is hardlinked to `outside/target.txt`.

State and persistence behavior: uses inode identity as the escape signal. The daemon may run as root when available; uid/gid lines are commented when not root.

Dependencies and integration points: daemon receiver alternate-basis lookup, secure relative open behavior, loopback test daemon, and filesystem symlinks/hardlinks.

Risks and test signals: if the daemon fails before creating the destination, the test fails as vacuous. A failure after creation means parent-symlink confinement was bypassed and daemon-readable outside content was used as basis.
