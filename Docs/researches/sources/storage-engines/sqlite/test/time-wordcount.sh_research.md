## sources/storage-engines/sqlite/test/time-wordcount.sh

### Purpose
`time-wordcount.sh` is a small shell benchmark driver for the `wordcount` test program. It runs the same input through multiple wordcount operation modes and table layouts to produce comparable timing summaries.

### Important APIs, types, and functions
The script uses POSIX shell, `rm -f`, and the local `./wordcount` executable. It forwards all user arguments after the required filename to `wordcount`, adding tags `A:` through `J:`, `--timer`, `--summary`, database names, operation flags, and optional `--without-rowid`.

### Control flow
The script requires at least one argument. It deletes `wcdb1.db` or `wcdb2.db` before insert/replace/select phases, runs rowid and `WITHOUT ROWID` variants for `--insert`, `--replace`, and `--select`, then runs query and delete phases against the generated databases. It removes both temporary databases at the end.

### State and persistence behavior
Only `wcdb1.db` and `wcdb2.db` are created, reused, and deleted. The source text is read by `wordcount`; this script does not inspect it directly. Timing and summaries are printed by child processes.

### Dependencies and integration points
It depends on a built `wordcount` executable in the current directory and standard shell utilities. It is intended as a manual performance comparison helper.

### Risks and test signals
The script does not use `set -e`, so a failed `wordcount` command does not automatically stop later phases. Filenames are passed through `$*`, so arguments with spaces are not preserved robustly. Signals are tagged timing lines from each phase and absence of leftover temporary database files after cleanup.
