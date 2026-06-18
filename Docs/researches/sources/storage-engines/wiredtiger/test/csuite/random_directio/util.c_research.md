# sources/storage-engines/wiredtiger/test/csuite/random_directio/util.c

Purpose: helper implementation for recursively copying a database directory, optionally using direct I/O for source reads, so `random_directio/main.c` can verify what is actually on disk.

Important APIs, types, and functions: defines `ALIGN_UP`, `ALIGN_DOWN`, `BUFFER_ALIGNMENT_DEFAULT`, `COPY_BUF_SIZE`, internal `copy_directory_int`, and exported `copy_directory`. It uses POSIX directory APIs (`opendir`, `readdir`, `closedir`), filesystem calls (`mkdir`, `open`, `fstat`, `read`, `write`, `close`), `O_DIRECT` when requested, and `testutil_remove` for destination cleanup.

Control flow: `copy_directory` removes the destination tree and calls `copy_directory_int`. The recursive helper creates the destination directory, iterates entries, skips `.`/`..`, recurses for directories, opens source files with `O_DIRECT` if requested, creates destination files normally, aligns the reusable buffer and read sizes to the source block size for direct I/O, copies file contents in chunks, and closes descriptors. If a source file disappears with `ENOENT`, it logs and skips it because WiredTiger drop can unlink before directory sync while the child is stopped.

State and persistence behavior: writes a complete destination directory tree, potentially omitting files that vanished during a concurrent drop. It allocates and frees a copy buffer per recursive call. Destination file permissions are created as `0666` subject to umask.

Dependencies and integration points: declared in `util.h` and linked into `test_random_directio`. It depends on `test_util.h`, platform `O_DIRECT`, `dirent.d_type` reporting directories, and WiredTiger utility macros such as `WT_MAX` and `WT_MIN`.

Risks: `dirent.d_type` can be `DT_UNKNOWN` on some filesystems, which this code does not stat-and-classify. Direct-I/O assumptions require aligned buffers and read sizes; the code asserts consistent block size after first allocation. It does not preserve metadata such as modes, ownership, or timestamps beyond creating files. Concurrent directory changes other than `ENOENT` can still assert.

Test signals: random-directio cycles succeeding under direct I/O validate this helper. The printed `COPY_DIR` `ENOENT` messages are expected only for files dropped during copy.
