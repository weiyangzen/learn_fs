# File Research: sources/virtualization/spdk/module/event/subsystems/vmd/vmd.c

Registers VMD support as an event subsystem.

Key elements:
- Maintains global `g_enabled` and hotplug poller pointer.
- Initializes VMD only when enabled by startup RPC.
- Calls `spdk_vmd_init()` and registers a periodic hotplug monitor poller.
- Fini unregisters the poller, calls `spdk_vmd_fini()`, and advances fini chain.
- Writes config JSON containing `vmd_enable` when enabled.
- Registers subsystem name `vmd`.

Dependencies:
- SPDK VMD, poller, init, JSON, and logging APIs.

Research notes:
- Hotplug monitor runs every 1,000,000 microseconds when enabled.
