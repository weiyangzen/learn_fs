# sources/test-tools/ltp/testcases/kernel/fs/fsplough/fsplough.c

## Purpose

`fsplough.c` writes randomized byte ranges to one test file through multiple I/O APIs and verifies the partial and final file contents against an in-memory oracle. It is intended to catch corruption or inconsistency across `write`, `pwrite`, `writev`, `pwritev`, `read`, `pread`, `readv`, `preadv`, normal cached I/O, and optional direct I/O.

## Important APIs, Types, and Functions

Important helpers are `fill_buffer`, `vectorize_buffer`, `update_filedata`, the four write wrappers, the four read wrappers, `open_testfile`, `setup`, `run`, and `cleanup`. Global state includes `read_fd`, `write_fd`, `writebuf`, `filedata`, filesystem `blocksize`, `bufsize`, `filesize`, command options `-c`, `-d`, `-W`, and `-R`, and the static `struct tst_test`.

## Control Flow

`setup` seeds randomness, optionally changes directory, parses loop count, opens the test file, gets `fstatvfs` block size, maps an aligned work buffer, and allocates the expected file image. `run` repeatedly fills random data, chooses a random aligned offset, updates the model, performs a random write API, reads the same range with a random read API, and compares. It then extends the file to the expected size, `fsync`s, drops caches, reopens for reading, and compares the whole file.

## State and Persistence Behavior

The persistent object is `fsplough.dat`, removed by cleanup. `filedata` is the authoritative in-memory state; `writebuf` is reused for both write and read verification. Direct I/O paths align sizes and offsets to the filesystem block size.

## Dependencies and Integration Points

It depends on the modern LTP `tst_test.h` API and `tst_safe_prw.h` wrappers, `/proc/sys/vm/drop_caches`, `mmap`, `statvfs`, vector I/O, and optional `O_DIRECT`.

## Risks and Edge Cases

`open_testfile` checks `(flags & O_RDONLY)` even though `O_RDONLY` is zero, so the `-R` direct-read option may not actually add `O_DIRECT`. Direct I/O alignment depends on `f_bsize` being accepted by the filesystem and device. The test is randomized, so a seed is not logged for exact replay.

## Test Signals

Strong pass signals are `TPASS` for sufficient loop execution, partial data consistency, and final data consistency. `TFAIL` pinpoints the mismatching byte range; `TWARN` reports an early timeout or very slow machine.
