# sources/test-tools/liburing/test/open-direct-link.c

Purpose: validates linked or drained direct open/read/close through fixed-file slot 0, including skipped success CQEs and async submission.

Important APIs/types/functions: `io_uring_prep_openat_direct`, `io_uring_prep_read`, `io_uring_prep_close_direct`, `io_uring_register_files`, `IOSQE_FIXED_FILE`, `IOSQE_IO_LINK`, `IOSQE_IO_DRAIN`, `IOSQE_CQE_SKIP_SUCCESS`, and `IOSQE_ASYNC`.

Control flow: registers eight fixed-file slots initialized to `-1`, creates `.link.direct`, then runs six combinations: link, drain, async link, async drain, skip-success link, and async skip-success link. Each sequence opens into slot 0, reads 4096 bytes via fixed file, and closes slot 0.

State and persistence behavior: creates `.link.direct` and unlinks it. Fixed-file slot 0 is repeatedly installed and closed.

Dependencies and integration points: requires fixed-file registration and `IORING_FEAT_CQE_SKIP`; skips if extra argument is provided or feature absent.

Risks and test signals: failures include bad open/read/close CQE results, unexpected CQE when success CQEs are skipped, or illegal drain/skip-success combination.
