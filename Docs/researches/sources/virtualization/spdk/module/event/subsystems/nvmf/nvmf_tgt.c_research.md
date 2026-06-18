# File Research: sources/virtualization/spdk/module/event/subsystems/nvmf/nvmf_tgt.c

Implements the NVMe-oF event subsystem lifecycle and optional NVMe admin passthrough behavior.

Key elements:
- Defines a target state machine from create target through poll group creation, subsystem start, running, and shutdown cleanup.
- Initializes default target options, discovery filter, DHCHAP digest/group masks, duplicate host policy, and admin passthrough flags.
- Creates one poll group thread per enabled core or per configured poll-group mask.
- Creates the discovery subsystem and starts/stops/destroys all NVMe-oF subsystems.
- Stops listeners before destroying subsystems and poll groups during shutdown.
- Implements custom admin command handlers for identify, get log page, get/set features, sanitize, security send/receive, firmware update, NVMe-MI, and vendor-specific commands.
- Passes allowed admin commands to a single-namespace bdev that supports `SPDK_BDEV_IO_TYPE_NVME_ADMIN`.
- Fixes selected identify/log-page data by merging NVMe drive data with SPDK NVMe-oF controller data.
- Writes config JSON for `nvmf_set_config`, DHCHAP options, duplicate host policy, poll group mask, and target config.

Dependencies:
- SPDK nvmf target APIs, bdev, thread, NVMe command structures, subsystem init/fini, and USDT probes.
- Depends on bdev, keyring, sock, accel, and iobuf subsystems.

Research notes:
- Shutdown requested during initialization is deferred until the target reaches a stable state.
- Admin passthrough is deliberately limited to single-namespace subsystems and requires NVMe admin support on the namespace bdev.
- Security send/receive passthrough logs a warning about key exposure unless transport encryption is used.
