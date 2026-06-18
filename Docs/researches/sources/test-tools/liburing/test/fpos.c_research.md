<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/fpos.c -->
## sources/test-tools/liburing/test/fpos.c

Purpose: verifies shared file-position (`f_pos`) handling for many linked reads and writes submitted with offset `-1`.

Important APIs/types/functions: `create_file`, `test_read`, `test_write`, `io_uring_prep_read`, `io_uring_prep_write`, `IOSQE_IO_LINK`, `IOSQE_ASYNC`, `io_uring_submit_and_wait`, and `lseek`.

Control flow: `main` runs eight combinations of read/write, async/non-async, and block size 1 or 7. Read tests submit 2048 linked reads at offset `-1`, reorder completions by `user_data`, validate alternating file data, and check `lseek` matches bytes read. Write tests submit 2048 linked one-byte writes at offset `-1`, verify file position equals queue size, then read back expected repeated data.

State and persistence behavior: temporary read/write files are unlinked after opening, so fd state persists without pathname. The file offset is shared mutable kernel state under heavy concurrent completions.

Dependencies and integration points: exercises implicit file-position updates, linked SQEs, async workers, and completion reordering.

Risks: assumes linked submission maintains enough ordering for `f_pos` semantics while completions may reorder. Failures show lost or duplicated offset advancement.

Test signals: pass means offset `-1` reads/writes advance `f_pos` coherently across large linked batches.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/fpos.c -->
