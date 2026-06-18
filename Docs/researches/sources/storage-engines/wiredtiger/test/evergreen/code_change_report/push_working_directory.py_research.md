<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/code_change_report/push_working_directory.py -->
# sources/storage-engines/wiredtiger/test/evergreen/code_change_report/push_working_directory.py

Purpose: provides a minimal cwd stack object for scripts that need to run relative shell/Git commands from a specific directory.

API: `PushWorkingDirectory(new_working_directory)` records `os.getcwd()` and immediately calls `os.chdir(new_working_directory)`. `pop()` changes back to the original directory.

Control flow and state: the object mutates process-global current working directory on construction and restoration. It does not implement context-manager methods, so callers must explicitly call `pop()`.

Dependencies and integration: used by `git_diff_tool.py` for `run_command()`, file scans, and deleted/renamed file discovery. A separate duplicate implementation exists in `code_coverage_utils.py`.

Risks and test signals: not exception-safe; an exception between construction and `pop()` leaves the process in the wrong directory. It is also unsafe for concurrent threads in the same process because cwd is process-wide. The class has no validation of target directory existence beyond `os.chdir()` exceptions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/code_change_report/push_working_directory.py -->
