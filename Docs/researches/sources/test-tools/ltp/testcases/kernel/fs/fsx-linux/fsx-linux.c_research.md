# sources/test-tools/ltp/testcases/kernel/fs/fsx-linux/fsx-linux.c

## Purpose

`fsx-linux.c` is a rewritten LTP file operation exerciser. It randomly applies reads, writes, truncates, mmap reads, and mmap writes to one test file while maintaining an in-memory expected file image.

## Important APIs, Types, and Functions

Important pieces are operation IDs `OP_READ` through `OP_MAPWRITE`, `struct file_pos_t`, `op_file_position`, `op_align_pages`, `update_file_size`, `memory_compare`, operation handlers `op_read`, `op_write`, `op_truncate`, `op_map_read`, `op_map_write`, plus `setup`, `run`, and `cleanup`. User options control max file size, max operation size, operation count, and write/read/truncate alignment.

## Control Flow

`setup` parses options, seeds `random()`, opens `ltp-file.bin`, and allocates `file_buff` and `temp_buff`. `run` resets file and buffers, then dispatches random operations until `op_nums` successful operations have completed. Read operations compare file data to the model, writes fill both model and temp buffers, truncation changes file size and zeroes the tail of the model, and mmap writes extend the file before mapping if needed.

## State and Persistence Behavior

The persistent file is `ltp-file.bin` in an LTP temporary directory. `file_buff` is the expected image and `file_size` is the current logical model size. The file descriptor stays open for the test lifetime and is closed during cleanup.

## Dependencies and Integration Points

Uses modern LTP `tst_test.h` safe wrappers, `mmap`, `msync`, `ftruncate`, `lseek`, read/write, and `sysconf(_SC_PAGESIZE)`.

## Risks and Edge Cases

`op_max_size` is parsed but not used when choosing operation sizes, so `-o` does not constrain operations. The random position code uses modulo arithmetic over `long long` sizes and can be biased. `cleanup` checks `if (file_desc)` even though fd 0 would be skipped, though `SAFE_OPEN` normally returns a positive descriptor in this context.

## Test Signals

The main pass signal is `TPASS "All file operations succeed"`. A memory comparison mismatch causes `TFAIL`, with `TDEBUG` identifying the first differing offset and bytes.
