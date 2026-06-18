# File Research: sources/virtualization/spdk/module/event/subsystems/vmd/event_vmd.h

Declares shared VMD event subsystem helpers.

Key elements:
- `vmd_subsystem_enable()` marks VMD enabled before subsystem init.
- `vmd_subsystem_is_enabled()` reports enable state.

Dependencies:
- Consumed by `vmd.c` and `vmd_rpc.c`.

Research notes:
- Minimal header for startup RPC to communicate enablement to subsystem init.
