# sources/test-tools/liburing/test/openat2.c

Purpose: tests `IORING_OP_OPENAT2` normal opens, direct fixed-file opens, invalid fixed slots, reinstalling over an existing fixed slot, and bad pointer errors.

Important APIs/types/functions: `struct open_how`, `io_uring_prep_openat2`, `io_uring_prep_openat2_direct`, `io_uring_register_files`, `io_uring_prep_write`, `io_uring_prep_read`, `IOSQE_FIXED_FILE`, `IOSQE_IO_LINK`, `pipe2(O_NONBLOCK)`, and `t_create_file`.

Control flow: opens absolute and relative paths with openat2, opens into fixed slot 0 and verifies write/read through that slot, checks direct open without a table returns `-ENXIO`, out-of-bounds and u16-overflow indexes return `-EINVAL`, reinstalls a file over pipe slot 1 and verifies pipe is not written, then tests bad path and bad `open_how` pointers expecting `-EFAULT`.

State and persistence behavior: creates `/tmp/.open.at2` and optionally `.open.at2`, then unlinks them. Fixed-file tables and a pipe table entry are mutated transiently.

Dependencies and integration points: depends on openat2 kernel support, fixed-file direct-open support, and filesystem permissions.

Risks and test signals: unsupported openat2 or fixed-open paths skip. Failures indicate wrong direct-slot validation, stale fixed-file slot content after reinstall, or missing bad-address checking.
