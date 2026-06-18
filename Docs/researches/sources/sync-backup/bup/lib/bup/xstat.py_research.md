## sources/sync-backup/bup/lib/bup/xstat.py

Purpose: provides enhanced stat/time helpers with nanosecond precision and portable wrappers for Cygwin UID/GID assertions.

Important APIs and control flow: time converters map between `(sec,nsec)`, timeval, integer filesystem nanoseconds, floor seconds, and printable seconds bytes. `utime()` and `lutime()` set nanosecond timestamps, with `lutime()` avoiding symlink following. On non-Cygwin platforms, `stat`, `fstat`, and `lstat` alias `os` functions; Cygwin wrappers assert nonnegative uid/gid. `mode_str()`, `classification_str()`, and `local_time_str()` render ls-like modes/classifiers/times.

State and dependencies: stateless; depends on `os`, `sys`, `time`, and Python `stat`. It integrates with metadata capture, `bup xstat`, `ls`, restore, and FUSE presentation.

Risks and tests: negative timestamp formatting adjusts seconds when nanoseconds are nonzero; symlink timestamp support depends on platform `os.utime(..., follow_symlinks=False)`. Tests include `test-fuse` for pre-epoch clamping in mounted output, `test-empty-metadata` for displayed modes, and repair tests that inspect `bup xstat`.
