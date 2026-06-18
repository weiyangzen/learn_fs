# sources/test-tools/cthon04/special/bigfile2.c

## Purpose
`bigfile2.c` targets sparse-file behavior around the 2 GiB and 4 GiB offset boundaries. It writes five bytes spanning each boundary and checks that file size and data readback remain correct with either native 64-bit offsets or Large File Summit transitional APIs.

## Important APIs, Types, and Functions
Important macros are `_LARGEFILE64_SOURCE`, `HIGH_WORD()`, `LOW_WORD()`, `LSEEK`, `FSTAT`, and the `offset64`/`stat_info` typedefs. Main logic is in `main()` and `check_around()`.

## Control Flow and State
If neither `NATIVE64` nor `_LFS64_LARGEFILE` is available, `main()` reports a skip and exits success. Otherwise it opens the file with `O_SYNC` and `O_LARGEFILE` when needed, checks around `0x80000000`, truncates to zero, then checks around `0x100000000`. `check_around()` seeks to `where - 2`, writes bytes `0` through `4`, verifies `st_size` after every byte, seeks back, and verifies each byte value.

## Persistence and Dependencies
Persistent state is a sparse test file that is unlinked at normal completion; failures may leave a huge sparse file name on disk. Dependencies: Large-file libc interfaces, `open`, `lseek64`/`lseek`, `fstat64`/`fstat`, `ftruncate`, `O_SYNC`, and `../tests.h`.

## Integration Points, Risks, and Test Signals
Integration is the special large-offset suite. Risks include platform macro detection drift, opening a named file destructively, sparse allocation surprises on filesystems without holes, and printf formatting that manually splits offsets. Test signals are skip output on 32-bit-only platforms, correct `st_size` at both boundaries, byte readback without mismatch, and final unlink.
