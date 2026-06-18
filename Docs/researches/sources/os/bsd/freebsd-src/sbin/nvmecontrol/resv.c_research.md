# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/resv.c

Purpose: Implements NVMe namespace reservation commands.

Key behavior:
- Registers `resv` with subcommands `acquire`, `register`, `release`, and `report`.
- Requires namespace device context for all subcommands.
- `acquire` submits `NVME_OPC_RESERVATION_ACQUIRE` with current/preempt keys, reservation type, and acquire action.
- `register` submits `NVME_OPC_RESERVATION_REGISTER` with current/new keys, register action, ignore-existing-key, and persist-through-power-loss change.
- `release` submits `NVME_OPC_RESERVATION_RELEASE` with key, type, and action.
- `report` submits `NVME_OPC_RESERVATION_REPORT`, supports normal and extended data structures, hex output, and verbose trimming behavior.

Dependencies:
- NVMe reservation structures and endian swap helpers.
- Shared `open_dev()`, `get_nsid()`, and `print_hex()`.

Research notes:
- Report output decodes generation, type, registered controller count, PTPL state, controller IDs, reservation status, host IDs, and keys.
- Command payloads are manually little-endian encoded before passthrough.
