# sources/test-tools/liburing/test/mock_file.h

Purpose: local ABI header for the io_uring mock-file manager and mock-file commands used by `mock_file.c`.

Important APIs/types/functions: feature enum values `IORING_MOCK_FEAT_*`, `struct io_uring_mock_probe`, `struct io_uring_mock_create`, manager command enums `IORING_MOCK_MGR_CMD_PROBE` and `IORING_MOCK_MGR_CMD_CREATE`, `IORING_MOCK_CMD_COPY_REGBUF`, and `IORING_MOCK_COPY_FROM`.

Control flow: header only; it defines constants and packed-like request structs consumed by `uring_cmd` SQEs.

State and persistence behavior: describes manager-visible fields such as feature bitmap, output fd, flags, mock file size, and artificial read/write delay. It has no executable state.

Dependencies and integration points: includes `<linux/types.h>` and is coupled to the kernel mock driver ABI and the liburing test program.

Risks and test signals: ABI drift between this header and the driver would surface as failed probe/create/copy commands in `mock_file.c`. Reserved fields preserve forward-compatible layout.
