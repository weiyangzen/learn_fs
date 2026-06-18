# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/getsize.c

Purpose: determines the byte size of an open block device or regular file.

Important APIs and control flow: `blkid_get_dev_size(fd)` tries platform-specific ioctls in preferred order: Darwin block count, Linux `BLKGETSIZE64` except old 2.5 kernels, legacy `BLKGETSIZE`, BSD `DIOCGMEDIASIZE`, floppy `FDGETPRM`, and disklabel partitions. For regular files it returns `st_size`. If all specialized methods fail, it performs exponential then binary search using `valid_offset()`, which seeks and reads one byte to find the last valid offset.

State and persistence: no persistent state; it changes the file descriptor offset during probing.

Dependencies and integration: used by probing code to bound reads. Depends on `blkid_llseek`, ioctl headers, `uname`, `fstat`, and platform disk headers.

Risks and test signals: binary search fallback can be slow or disruptive for unusual devices, and old-kernel checks are heuristic. Test block devices, regular files, zero-length files, old ioctl failures, large devices beyond 32-bit offsets, and final fd offset expectations.
