# sources/test-tools/ltp/testcases/kernel/syscalls/fallocate/fallocate04.c

Purpose: Filesystem-wide test of advanced `fallocate()` modes: punch hole, zero range, collapse range, and insert range.

Important APIs/types/functions: `fallocate`, `FALLOC_FL_PUNCH_HOLE`, `FALLOC_FL_ZERO_RANGE`, `FALLOC_FL_COLLAPSE_RANGE`, `FALLOC_FL_INSERT_RANGE`, `lseek(SEEK_HOLE)`, `fstat`, `fsync`, and buffer comparisons.

Control flow: The test allocates and writes a 3-block file, then sequential subtests punch the middle block, zero a range, collapse a block, and insert a block, checking allocated size and file data after each operation.

State and persistence behavior: State is mounted test filesystem data, allocated block count, file contents, and file size. Subtests are intentionally ordered because each mutates the same file.

Dependencies and integration points: Requires root, a mounted test device, all-filesystems coverage, and optional verbose hex dumps.

Risks and test signals: Mode support varies by filesystem and returns `TCONF` for `EOPNOTSUPP`. Because subtests mutate shared state, an early failure can affect later cases.
