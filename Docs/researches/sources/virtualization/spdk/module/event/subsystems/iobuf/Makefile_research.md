# File Research: sources/virtualization/spdk/module/event/subsystems/iobuf/Makefile

Builds the event iobuf subsystem library.

Key elements:
- Compiles `iobuf.c` and `iobuf_rpc.c`.
- Produces `event_iobuf`.
- Uses shared object version `5.0`.
- Uses the blank SPDK map file.

Dependencies:
- Provides both lifecycle integration and RPC option/stat support.

Research notes:
- Many other event subsystems depend on iobuf for buffer-pool availability.
