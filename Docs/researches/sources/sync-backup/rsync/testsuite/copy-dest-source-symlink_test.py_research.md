# sources/sync-backup/rsync/testsuite/copy-dest-source-symlink_test.py

Purpose: daemon security regression for `--copy-dest` source opens escaping through a parent symlink in the alternate-destination path.

Important APIs/types/functions: daemon config, `start_test_daemon`, `rsync_argv('-rtp', '--copy-dest=cd')`, `filecmp.cmp`, uid/gid helpers, and scratch path setup.

Control flow: create module, outside directory, and source. Plant `module/cd -> outside`; make source `target.txt` same size/mtime/mode as outside but with different content. Push to daemon with `--copy-dest=cd`, then require destination exists, does not match outside content, and does match source content.

State and persistence behavior: content equality, not inode identity, is the oracle because copy-dest copies basis bytes. Outside content must never be read into module output.

Dependencies and integration points: daemon receiver copy-altdest path, secure source open behavior, and loopback daemon.

Risks and test signals: if destination is absent the test fails as vacuous. Matching outside content is a direct read-disclosure/escape signal.
