# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/util/copy_sparse.c

Purpose: `copy_sparse.c` copies sparse files efficiently on Linux by using block mapping to skip holes. On non-Linux it exits with an unsupported message.

Important APIs, types, and functions: `get_bmap()` wraps the Linux `FIBMAP` ioctl; `full_read()` retries reads and handles interruptions; `copy_sparse_file()` performs the copy; `usage()` and `main()` parse `-v source destination`. It uses large-file APIs (`stat64`, `open` with `O_LARGEFILE`, `lseek64`), `FIGETBSZ`, and root-only `FIBMAP`.

Control flow: for regular source files, it stats and opens the source, obtains filesystem block size via `FIGETBSZ`, and computes block count. For stdin (`-`), it uses fd 0 with a 1024-byte block size. The destination is opened/truncated. For each source block, file input uses `FIBMAP` to skip unmapped blocks; stdin scans zero-filled blocks to preserve holes. Non-hole data is read and written, seeking the destination over skipped ranges. At the end it ensures destination size reaches the source size by seeking and writing a final zero if needed.

State and persistence: reads source data and creates/replaces the destination file with mode `0777` subject to umask. It may create sparse holes via seeks. It does not preserve ownership, mode, timestamps, xattrs, or ACLs.

Dependencies and integration points: Linux-only path depends on kernel ioctls from `<linux/fd.h>` and root permissions for `FIBMAP`. The util Makefile has a target for it but does not build it by default.

Risks: `fileinfo` is uninitialized in the stdin path, but later `offset = fileinfo.st_size` is executed unconditionally, which is a correctness bug if copying from stdin. Many read/write/lseek calls have incomplete error handling; short writes are detected only by comparing one `write()` result. `FIBMAP` requires privileges and may not work on modern filesystems or with delayed allocation. Destination permissions are overly broad before umask. It does not use newer `SEEK_HOLE`/`SEEK_DATA`.

Test signals: test sparse file logical size and block usage before/after copy, compare file contents, run as non-root to verify permission error handling, and test stdin path because it has distinct control flow and likely size-finalization issues.
