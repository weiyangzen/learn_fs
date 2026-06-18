# File Research: sources/virtualization/spdk/module/event/subsystems/fsdev/fsdev.c

Registers the SPDK fsdev framework as an event subsystem.

Key elements:
- Initializes through `spdk_fsdev_initialize()`.
- Finishes through `spdk_fsdev_finish()`.
- Emits fsdev config JSON through `spdk_fsdev_subsystem_config_json()`.
- Registers subsystem name `fsdev`.

Dependencies:
- Uses SPDK fsdev, env, thread, and init APIs.

Research notes:
- No explicit subsystem dependencies are declared in this file.
