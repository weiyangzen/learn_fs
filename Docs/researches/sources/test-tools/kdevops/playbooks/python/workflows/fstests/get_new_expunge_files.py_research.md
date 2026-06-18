# sources/test-tools/kdevops/playbooks/python/workflows/fstests/get_new_expunge_files.py

Purpose: Lists expunge files for a filesystem that are not tracked by git.

Key APIs and flow: `main()` parses filesystem and expunge directory, walks all files, filters paths containing the filesystem string, calls `git.is_new_file()`, strips a leading `../` segment for display, and prints new files.

State, dependencies, integration: Reads the filesystem and invokes local `lib.git`, which shells out to `git status -s`. It writes only stdout and is meant to help identify newly generated expunge sections.

Risks and test signals: Filtering uses substring matching across the full path, which can include false positives; `subprocess` and `pwd` are unused; a git timeout returns the string `"Timeout"`, which is truthy and will be printed as if new. Tests should mock `git.is_new_file()`, cover timeout behavior, `../` shortening, missing directories, and filesystem names that appear in parent paths.
