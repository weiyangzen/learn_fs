# File Research: sources/virtualization/spdk/module/event/subsystems/ublk/ublk.c

Registers the SPDK ublk service as an event subsystem.

Key elements:
- Initializes through `spdk_ublk_init()`.
- Finishes asynchronously through `spdk_ublk_fini()`, with fallback completion if fini returns an error.
- Writes config JSON through `spdk_ublk_write_config_json()`.
- Registers subsystem name `ublk`.

Dependencies:
- Declares dependencies on `bdev` and `iobuf`.

Research notes:
- Provides Linux ublk integration for exposing SPDK bdevs.
