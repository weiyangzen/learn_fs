# File Research: sources/virtualization/spdk/module/event/Makefile

Top-level build dispatcher for event subsystem modules.

Key elements:
- Builds only the `subsystems` directory.
- Uses SPDK common and subdirs make fragments.
- Defines `all` and `clean` phony targets.

Dependencies:
- Delegates subsystem library selection to `module/event/subsystems/Makefile`.

Research notes:
- This is directory orchestration, not a direct source build unit.
