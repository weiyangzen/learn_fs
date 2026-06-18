# sources/test-tools/liburing/test/rename.c

Purpose: tests the io_uring rename operation for successful path replacement and error propagation for nonexistent paths and bad user pointers.

Important APIs and types: `io_uring_prep_rename`, `io_uring_submit`, `io_uring_wait_cqe`, `mkstemp`, `stat`, `unlink`, and standard errno results `ENOENT` and `EFAULT`. The file manually clears SQEs with `memset()` before preparation.

Control flow: `main()` creates two temporary files in the current directory and verifies both exist. `test_rename()` submits a rename from source to destination and returns the CQE result. If the first rename returns `-EBADF` or `-EINVAL`, rename support is treated as unavailable and the test skips the rest. Otherwise, the source must disappear and destination must exist. It then submits a rename for two invalid absolute paths and requires `-ENOENT`. Finally, `test_rename_badaddr()` submits one case with an invalid new path pointer and one with an invalid old path pointer, both expected to return `-EFAULT`.

State and persistence: filesystem state is persistent across calls: the first successful rename removes `src` and replaces `dst`. Cleanup unlinks `dst` on success/skip and both names on error.

Dependencies and integration: requires kernel support for `IORING_OP_RENAME` and a writable current directory. Extra argv exits success for harness behavior.

Risks and test signals: failures indicate rename support returns wrong errors, bad pointers are not rejected safely, or filesystem state after rename is wrong. Passing confirms successful operation and key error paths.
