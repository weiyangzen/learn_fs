# sources/sync-backup/rsync/testsuite/daemon-groupmap-wild_test.py

Purpose: regression for issue #829 where daemon option argument escaping caused `--groupmap=*:<gid>` wildcard to be treated literally.

Important APIs/types/functions: group selection via `grp` or `os.getgroups`, `check(label, *extra_opts)`, `write_daemon_conf`, `start_test_daemon`, `rsync_argv('-rg', '--groupmap=*:<gid>')`, and `os.stat`.

Control flow: choose two usable group IDs, start writable daemon, then run two uploads: default args and `--secluded-args`. Each creates a source file with source group, uploads with wildcard groupmap, and asserts destination gid equals target group.

State and persistence behavior: destination file group ID is the oracle. Source/module directories are reset before each subcase.

Dependencies and integration points: daemon argument parsing/unescaping, groupmap receiver logic, safe_arg behavior, secluded args, and host group permissions.

Risks and test signals: skips when fewer than two usable groups exist. Failure means wildcard was ignored or escaped incorrectly over daemon protocol.
