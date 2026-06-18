# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/selftest.c

Purpose: Implements `nvmecontrol selftest`.

Key behavior:
- Registers top-level `selftest`.
- Requires `--test-code`.
- Opens controller or namespace, normalizing namespace paths to controller paths while preserving NSID.
- Validates test code is `0x0` through `0xf`.
- Reads controller identify data and checks `NVME_CTRLR_DATA_OACS_SELFTEST`.
- Submits `NVME_OPC_DEVICE_SELF_TEST`.
- Special-cases command-specific “self-test in progress” status to return `EX_UNAVAILABLE`.

Dependencies:
- `read_controller_data()`, `open_dev()`, and `get_nsid()`.
- NVMe self-test opcode/status constants.

Research notes:
- Supports both controller/global and namespace-specific self-test contexts depending on supplied device.
