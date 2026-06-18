# File Research: sources/virtualization/spdk/module/event/subsystems/iscsi/iscsi.c

Registers the SPDK iSCSI target as an event subsystem.

Key elements:
- Initializes via `spdk_iscsi_init()`.
- Finishes via `spdk_iscsi_fini()`.
- Writes config JSON through `spdk_iscsi_config_json()`.
- Registers subsystem name `iscsi`.

Dependencies:
- Declares dependencies on `scsi` and `sock`.

Research notes:
- Uses asynchronous init/fini completion callbacks to advance the subsystem chain.
