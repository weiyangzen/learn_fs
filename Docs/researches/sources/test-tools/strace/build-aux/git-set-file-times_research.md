<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/build-aux/git-set-file-times -->
# sources/test-tools/strace/build-aux/git-set-file-times

Purpose: Perl utility that sets tracked file mtimes/atimes to their latest Git commit time, useful before building from rsync or fresh checkouts.

Important logic: accepts optional `--prefix=...`, finds Git top-level, records all tracked files from `git ls-files -z`, then streams `git log -r --name-only --no-color --pretty=raw -z`. For each commit time and file list, it removes not-yet-set files from the hash and calls `utime` with that commit time, stopping once all files are handled.

Control flow: newest commits are processed first, so first time a file appears is its latest commit. Prefix is prepended before `utime`.

State and persistence: mutates filesystem timestamps for tracked files.

Dependencies and integration: Perl, Git, and repository working tree. It supports reproducible archive/build timestamp workflows.

Risks: timestamp mutation can confuse incremental builds if run at the wrong time. Prefix must match the target tree layout. Test signals: run in a disposable checkout and compare selected file mtimes with `git log -1 --format=%ct -- file`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/build-aux/git-set-file-times -->
