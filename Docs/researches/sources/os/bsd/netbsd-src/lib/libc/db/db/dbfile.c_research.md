# File Research: sources/os/bsd/netbsd-src/lib/libc/db/db/dbfile.c

Provides shared file-opening helpers for DB access methods. `__dbopen` wraps `open`, forces close-on-exec using `O_CLOEXEC` or `fcntl(FD_CLOEXEC)`, optionally fills a `stat` buffer, and preserves `errno` if cleanup is needed.

`__dbtemp` creates an unlinked temporary file using `TMPDIR` when safe, otherwise `_PATH_TMP`. It blocks signals around `mkstemp`, `unlink`, `fcntl(FD_CLOEXEC)`, and optional `fstat` to avoid leaking a named temporary file on interruption.

Dependencies include POSIX file APIs, signals, paths, and `<db.h>`. Hash uses `__dbtemp` for anonymous backing storage; btree/recno use `__dbopen` for database or record files.

Risks/invariants: `__dbtemp` ignores `TMPDIR` under `issetugid`. It returns an open fd whose path has already been unlinked, so later persistence is impossible unless another layer copied data elsewhere.
