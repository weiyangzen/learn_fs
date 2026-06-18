## sources/sync-backup/rsync/testsuite/omit-times_test.py

Purpose: verifies `-O` omits directory mtimes while preserving file mtimes, and `-J` omits symlink mtimes where supported.

Important APIs and control flow: `seed()` builds a depth-3 tree and sets all file and directory mtimes to a fixed old timestamp. With `run_rsync('-rlt', '-O')`, every file mtime must match `OLD` while every directory mtime must differ. For `-J`, it creates a deep symlink, attempts to set its mtime with `follow_symlinks=False`, skips that subcheck when unsupported, then requires copied symlink mtime not to equal `OLD`.

State and dependencies: uses `os.utime`, symlink support, `walk_files`, `walk_dirs`, and mtime assertions.

Integration points: covers receiver time-setting exclusions for directories and symlinks.

Risks and test signals: symlink mtime portability is explicitly handled. Directory checks require every directory to omit times, catching partial regressions.
