## sources/sync-backup/rsync/testsuite/ownership-depth_test.py

Purpose: verifies group and owner remapping options at depth, with root and non-root paths.

Important APIs and control flow: declares `fleet_nonroot = True` so fleet runs it as a normal user too. `seed()` builds a depth-3 tree and normalizes source group to the primary gid. `assert_all()` checks uid/gid for every destination entry. As root it tests numeric and wildcard `--groupmap`, named/nameless empty-source group mapping, `--chown`, `--usermap`, and combined user/group chown. As non-root it uses a secondary group for group-only remaps and skips user remap.

State and dependencies: depends on user/group IDs, `grp`, `rsync_getgroups`, privilege helpers, and filesystem ownership changes.

Integration points: covers idlist mapping, archive ownership application, numeric IDs, and fleet non-root discovery.

Risks and test signals: highly environment-sensitive. Skip paths handle missing secondary groups. Signals are uid/gid equality over all files and directories.
