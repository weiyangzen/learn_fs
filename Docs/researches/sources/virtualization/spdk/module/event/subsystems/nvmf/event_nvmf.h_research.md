# File Research: sources/virtualization/spdk/module/event/subsystems/nvmf/event_nvmf.h

Defines shared NVMe-oF event subsystem configuration types and globals.

Key elements:
- `struct spdk_nvmf_admin_passthru_conf` controls which admin commands may be passed through.
- `struct spdk_nvmf_tgt_conf` wraps target options plus admin passthrough config.
- Externs expose `g_spdk_nvmf_tgt_conf`, `g_spdk_nvmf_tgt`, and `g_poll_groups_mask`.

Dependencies:
- Includes SPDK nvmf, queue, init, and log headers.

Research notes:
- Shared by `nvmf_tgt.c` and `nvmf_rpc.c`.
