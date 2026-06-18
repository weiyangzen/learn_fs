# File Research: sources/virtualization/spdk/module/event/subsystems/accel/accel.c

Registers the SPDK accel framework as an event subsystem.

Key elements:
- Initializes via `spdk_accel_initialize()`.
- Finishes asynchronously via `spdk_accel_finish()`.
- Exposes config JSON through `spdk_accel_write_config_json`.
- Registers subsystem name `accel`.

Dependencies:
- Depends on `iobuf` through `SPDK_SUBSYSTEM_DEPEND(accel, iobuf)`.

Research notes:
- The subsystem simply bridges framework lifecycle callbacks into the event subsystem init/fini chain.
