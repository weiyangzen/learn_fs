# File Research: sources/virtualization/spdk/module/event/subsystems/vmd/vmd_rpc.c

Adds JSON-RPC control for VMD.

Key elements:
- Registers startup RPC `vmd_enable`.
- Registers runtime RPC `vmd_remove_device`, decoding a PCI address and calling `spdk_vmd_remove_device()`.
- Registers runtime RPC `vmd_rescan`, returning the number of devices found.
- Rejects remove/rescan requests when VMD is disabled.

Dependencies:
- Uses `event_vmd.h`, SPDK VMD, env, PCI address parsing, JSON-RPC, and generated RPC context helpers.

Research notes:
- Device removal and rescan require prior startup-time enablement.
