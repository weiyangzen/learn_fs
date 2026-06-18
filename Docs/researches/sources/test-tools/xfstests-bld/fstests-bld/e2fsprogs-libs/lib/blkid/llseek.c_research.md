# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/llseek.c

Purpose: abstracts large-file seek support for libblkid across old Linux and non-Linux systems.

Important APIs and control flow: `blkid_llseek(fd, offset, whence)` uses normal `lseek` when `off_t` can represent the requested offset. On Linux it prefers `lseek64`, then `llseek`, then the `_llseek` syscall wrapper where needed. If an old kernel lacks `_llseek`, a static `do_compat` flag suppresses future attempts and returns `EOVERFLOW`. Non-Linux builds use `lseek64` when available or reject unrepresentable offsets with `EOVERFLOW` before falling back to `lseek`.

State and persistence: Linux fallback stores `do_compat` process-wide after `ENOSYS`. It mutates the fd offset.

Dependencies and integration: used by `getsize.c` and block probing reads. Depends on large-file feature macros, syscall headers, errno, and configured type sizes.

Risks and test signals: old syscall declarations and 32-bit boundary logic are platform-sensitive. Test offsets below/above 2 GiB, ENOSYS fallback, non-Linux `lseek64`, `EOVERFLOW`, and preservation of errno semantics.
