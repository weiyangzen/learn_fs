# File Research: sources/virtualization/spdk/module/event/subsystems/iscsi/Makefile

Builds the event iSCSI subsystem library.

Key elements:
- Adds `-I$(SPDK_ROOT_DIR)/lib` to CFLAGS.
- Compiles `iscsi.c`.
- Produces `event_iscsi`.
- Uses shared object version `8.0`.

Dependencies:
- Uses blank SPDK map file and library make fragment.

Research notes:
- Runtime dependencies are declared in `iscsi.c`.
