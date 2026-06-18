## sources/security-integrity/ecryptfs-utils/tests/kernel/mmap-bmap/test.c

Purpose: C comparator for lower and upper block maps. It checks that every block number returned for the eCryptfs upper file also appears in the lower encrypted file and that the upper file does not report more blocks than the lower file.

Important APIs and functions: `get_blocks`, `check_blocks`, `main`, `open`, `ioctl(FIGETBSZ)`, `fstat`, `ioctl(FIBMAP)`, `malloc/free`. Control flow reads block size and file size, computes block counts, gathers block numbers for both files, then performs nested membership checks.

State and persistence: Allocates transient arrays of block numbers; no writes. Dependencies are Linux `linux/fs.h` ioctls and filesystems supporting or at least tolerating `FIBMAP`. Integration is via `mmap-bmap.sh`. Risks: `FIBMAP` failures are silently represented as block `0`, so unsupported filesystems can mask or distort failures. The test signal is `EXIT_SUCCESS` for subset relation, `EXIT_FAILURE` for open/stat/ioctl allocation failures or mismatched mappings.
