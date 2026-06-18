# sources/distributed-fs/tahoe-lafs/src/allmydata/test/cli/test_mv.py

## Purpose
This module tests `tahoe mv` command semantics: renaming, overwriting files, moving into directories with trailing slash, nested path behavior, DELETE failure handling, and user-friendly alias errors.

## Important APIs, Types, and Functions
- `Mv.test_mv_behavior` is the main end-to-end scenario.
- `Mv.test_mv_error_if_DELETE_fails` monkey-patches `tahoe_mv.do_http` to simulate a failed source deletion after copy/link work.
- `test_mv_without_alias` and `test_mv_with_nonexistent_alias` validate validation of both source and target aliases.

## Control Flow
The main test creates two local files, uploads them, renames `file1` to `file3`, overwrites `file2`, creates a remote directory, checks that moving a file to a directory without trailing slash is rejected, then moves into the directory with a slash. It verifies the moved file exists at the destination and the old path returns 404. It also builds nested directories and ensures moving a nested file into another directory moves only the file, not an ancestor directory.

## State and Persistence Behavior
The tests persist local files and remote grid files/directories under a `tahoe` alias. Remote state is mutated by `mv`: source links should disappear, target links should appear or be overwritten, and directories should remain directories. The DELETE failure test temporarily replaces module-level `tahoe_mv.do_http` and restores it with `addBoth`.

## Dependencies and Integration Points
The module depends on `fileutil`, `GridTestMixin`, `CLITestMixin`, and `allmydata.scripts.tahoe_mv`. It uses other CLI commands (`create-alias`, `cp`, `mkdir`, `get`, `put`) to set up and verify move behavior.

## Risks and Edge Cases
Key risks are directory overwrite protection, trailing slash interpretation, nested destination basename selection, incomplete moves when DELETE fails, and validation order for missing aliases. The DELETE mock ensures the CLI does not print success or return a success code when cleanup fails.

## Test Signals
Signals are practical end-to-end assertions against remote behavior and HTTP failure injection. Coverage is narrower than `cp`, but it targets the high-risk semantics for a move operation.
