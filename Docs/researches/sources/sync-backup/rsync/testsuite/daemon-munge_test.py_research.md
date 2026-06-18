# sources/sync-backup/rsync/testsuite/daemon-munge_test.py

Purpose: daemon coverage for `munge symlinks = yes`, ensuring symlinks are stored safely with `/rsyncd-munged/` and unmunged on download.

Important APIs/types/functions: `make_tree`, `assert_is_symlink`, `write_daemon_conf`, `start_test_daemon`, `rsync_argv('-al')`, and `os.readlink`.

Control flow: create depth-3 source with deep symlink `d1/d2/sl -> f3`, configure writable munge module, push with links preserved and verify stored symlink target is `/rsyncd-munged/f3`. Then pull back and verify output symlink target is `f3`.

State and persistence behavior: module backing directory stores munged symlink target; pulled directory stores unmunged target.

Dependencies and integration points: daemon symlink munging, sender/receiver link handling, and symlink assertions.

Risks and test signals: failures mean unsafe symlink storage or missing unmunge on read.
