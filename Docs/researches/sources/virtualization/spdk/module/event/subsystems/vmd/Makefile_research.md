# File Research: sources/virtualization/spdk/module/event/subsystems/vmd/Makefile

Builds the VMD event subsystem library.

Key elements:
- Compiles `vmd.c` and `vmd_rpc.c`.
- Produces `event_vmd`.
- Uses shared object version `8.0`.
- Uses blank SPDK map file.

Dependencies:
- Provides both VMD lifecycle and RPC control.

Research notes:
- The VMD subsystem is disabled by default and enabled through startup RPC.
