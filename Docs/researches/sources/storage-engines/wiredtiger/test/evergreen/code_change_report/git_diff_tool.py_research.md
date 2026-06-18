<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/code_change_report/git_diff_tool.py -->
# sources/storage-engines/wiredtiger/test/evergreen/code_change_report/git_diff_tool.py

Purpose: produces a Git diff file suitable for pygit2 parsing by excluding newly added empty files, deleted files, and renames involving empty files. This works around pygit2 failures on diffs for newly added zero-length files.

Important APIs: `run_command(directory, command)` temporarily changes cwd and runs a shell command. `get_merge_base_commit()` finds `git merge-base develop HEAD`. `find_zero_length_files()` scans the worktree. `find_deleted_files()` and `find_moved_zero_length_files()` use Git name-status filters. `create_diff_file()` combines exclusions into `:(exclude)` pathspecs and writes `git diff <merge-base> -- ...`.

Control flow: `main()` accepts `--git_root`, `--git_diff_file`, and `--verbose`, then delegates to `create_diff_file()`.

State and persistence: reads worktree and Git history; writes a diff file with a trailing newline. It changes process cwd through `PushWorkingDirectory`.

Dependencies and integration: used by coverage and per-test coverage scripts before `Diff.parse_diff()`. Depends on `git`, pygit2 repository discovery, shell pathspec handling, and a branch named `develop`.

Risks and test signals: `subprocess.run(..., shell=True)` and hand-built command strings make quoting important. Large exclusion lists can exceed command-line length. The helper is not exception-safe if `run_command` fails before `pop()`. Renamed file parsing assumes three whitespace-separated fields.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/code_change_report/git_diff_tool.py -->
