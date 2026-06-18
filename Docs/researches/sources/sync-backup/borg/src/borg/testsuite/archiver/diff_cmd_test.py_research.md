# sources/sync-backup/borg/src/borg/testsuite/archiver/diff_cmd_test.py

Purpose: comprehensive integration tests for `borg diff`, covering text and JSON output for file content changes, metadata changes, symlinks, hardlinks, directories, sorting, content-only mode, timestamp differences, and hardlink deletion/replacement edge cases.

Important APIs/types/functions: `test_basic_functionality` contains nested `do_asserts` and `do_json_asserts` helpers. Other tests cover `--format`, `--sort-by`, invalid sort fields, every sort key/direction, and hardlink-specific behavior. Shared helpers include `cmd`, `create_regular_file`, `assert_line_exists`, `assert_line_not_exists`, `granularity_sleep`, and platform capability probes.

Control flow: the main test builds snapshot `test0` with empty/unchanged/removed/replaced/touched files, directories, symlinks, and hardlinks, mutates the tree extensively, then creates two second snapshots with different chunking. It compares archives in normal, content-only, and JSON-lines modes and asserts exact change categories while excluding unchanged or symlink-target-only cases. Sorting tests create controlled removed/changed/added files and assert order or valid coverage for sort keys. Timestamp tests distinguish recreated files from chmod-only metadata changes across Windows/POSIX. Hardlink tests compare deletion and recreation with and without patterns, verifying ctime-only hints and absence of false content changes.

State and persistence behavior: creates multiple archives from mutating input trees. Uses filesystem timestamps, modes, symlinks, hardlinks, and content sizes as diff inputs. No direct repository mutation.

Dependencies and integration points: covers diff command, archive item comparison, hardlink identity semantics, pattern engine, JSON output schema, sort-key implementation, platform timestamp behavior, and archive creation.

Risks: many assertions depend on exact human output phrasing/spacing and platform-specific metadata availability. Hardlink behavior differs on unsupported or problematic platforms, so skip conditions exclude FreeBSD/NetBSD/Windows for one case.

Test signals: strong behavioral coverage that diff reports meaningful changes, suppresses irrelevant changes in content-only mode, emits valid JSON changes, and maintains deterministic sorting.
