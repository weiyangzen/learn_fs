# sources/test-tools/fio/oslib/linux-dev-lookup.c

Purpose: recursively resolves a block device path from major/minor numbers for blktrace replay.

Important APIs/functions: `blktrace_lookup_device(const char *redirect, char *path, unsigned int maj, unsigned int min)`.

Control flow: if `redirect` is provided, it copies it to `path` and succeeds. Otherwise it opens the directory named by `path`, iterates entries, recursively descends into directories, and compares `major(st.st_rdev)`/`minor(st.st_rdev)` for block devices. On match, it copies the found full path back to `path`.

State and persistence: no persistent state; mutates the caller's `path` buffer during recursive search.

Dependencies and integration: Linux `stat`, `sysmacros`, directory APIs, and blktrace replay code that records device major/minor.

Risks: `full_path[257]` and `strcpy()`/`sprintf()` make path length assumptions and can overflow/truncate in deep trees. Recursion follows directories without cycle protection beyond normal filesystem constraints. `redirect` copy also assumes caller buffer is large enough.

Test signals: lookup existing and missing block devices under `/dev`, redirect override, deep directory paths, and path-buffer sizing.
