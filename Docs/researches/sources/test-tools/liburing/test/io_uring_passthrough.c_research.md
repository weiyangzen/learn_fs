<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/io_uring_passthrough.c -->
## sources/test-tools/liburing/test/io_uring_passthrough.c

Purpose: NVMe passthrough read/write test matrix for `IORING_OP_URING_CMD` with SQE128/CQE32 rings.

Important APIs/types/functions: `verify_buf`, `fill_pattern`, `__test_io`, `test_io`, `test_invalid_passthru_submit`, `test_io_uring_submit_enters`, `io_uring_prep_uring_cmd`, `NVME_URING_CMD_IO`, `NVME_URING_CMD_IO_VEC`, `IORING_URING_CMD_FIXED`, and NVMe fields from `nvme.h`.

Control flow: the test expects an NVMe block device path. It builds NVMe read/write commands over a 256 KiB buffer matrix, varying read/write, SQPOLL fixed files, registered buffers, vector vs non-vector command payloads, hybrid IOPOLL, async, and linked NOP chains. It verifies read data patterns, tests an invalid namespace submission failure, and checks submit behavior on IOPOLL passthrough rings.

State and persistence behavior: global data/meta buffers and NVMe namespace geometry drive command construction. `no_pt` and `vec_fixed_supported` gate unsupported passthrough variants.

Dependencies and integration points: requires NVMe uring command support, SQE128/CQE32, optional metadata handling, IOPOLL, fixed files, and registered buffers.

Risks: highly hardware-specific and commonly skipped without NVMe passthrough support. Incorrect LBA/metadata calculations can produce device errors.

Test signals: pass means passthrough commands operate correctly across command layouts and ring modes.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/io_uring_passthrough.c -->
