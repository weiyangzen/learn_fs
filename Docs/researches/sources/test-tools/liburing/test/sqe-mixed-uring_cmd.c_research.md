# sources/test-tools/liburing/test/sqe-mixed-uring_cmd.c

Purpose: combines normal NOP SQEs with 128-byte NVMe passthrough `uring_cmd` SQEs under mixed SQE/CQE setup.

Important APIs/types/functions: `IORING_SETUP_CQE_MIXED`, `IORING_SETUP_SQE_MIXED`, `io_uring_prep_uring_cmd128`, `NVME_URING_CMD_IO`, `struct nvme_uring_cmd`, `nvme_get_info`, `nvme_cmd_read`, `lba_shift`, and `nsid`.

Control flow: requires a device path argument, verifies it is an NVMe character device with `nvme_get_info`, initializes a mixed SQE/CQE ring, then loops 32 times alternating normal NOP submissions and NVMe read passthrough commands into a static 4 KiB buffer.

State/persistence behavior: reads from an NVMe namespace but does not write. Global NVMe metadata from `nvme.h` shapes the command.

Dependencies/integration: depends on NVMe passthrough support, device permissions, character-device path, and mixed SQE/CQE kernel support. Missing prerequisites skip.

Risks/test signals: detects mixed SQE corruption, passthrough command failure, wrong CQE result, wrong user data, or incompatible device metadata.
