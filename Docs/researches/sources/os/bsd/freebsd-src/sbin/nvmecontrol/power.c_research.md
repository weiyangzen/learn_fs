# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/power.c

Purpose: Implements `nvmecontrol power` for listing, showing, and setting NVMe power management state.

Key behavior:
- Registers top-level `power`.
- `--list` reads controller identify data and prints supported power states with max power, latencies, relative read/write throughput/latency, idle power, active power, and workload.
- `--power` submits `NVME_OPC_SET_FEATURES` for `NVME_FEAT_POWER_MANAGEMENT`.
- Without `--list` or `--power`, submits `NVME_OPC_GET_FEATURES` and prints current power state and workload hint.
- Normalizes namespace devices to controller devices before controller-level operations.

Dependencies:
- `read_controller_data()`, `open_dev()`, and `get_nsid()`.
- NVMe feature passthrough through `NVME_PASSTHROUGH_CMD`.

Research notes:
- The file has a static assertion that `struct nvme_power_state` has the expected 32-byte size.
