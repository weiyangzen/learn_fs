# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mac_provider.h

Purpose: Defines the GLDv3 MAC provider interface used by network drivers to register links, advertise capabilities, expose callbacks, and interact with MAC-layer rings, groups, offloads, VLAN handling, transceivers, and LEDs.

Key interfaces:
- Versioning: `MAC_VERSION_V1`, `MAC_VERSION`.
- Capability enum: checksum, LSO, rings, shares, multiple factory addresses, VNIC/aggr/VRRP/overlay/transceiver/LED capabilities.
- Driver callbacks: `mac_callbacks_t` and `MC_*` flags for optional callbacks.
- Ring/group capability structures: `mac_capab_rings_t`, `mac_ring_info_t`, `mac_group_info_t`.
- Registration: `mac_register_t`, `mac_alloc()`, `mac_register()`, `mac_unregister()`.
- Data path notifications: `mac_rx()`, `mac_rx_ring()`, link/unicast/TX/capability update calls.
- Packet offload inspection: `mac_ether_offload_info_t`, `mac_ether_l2_info()`, `mac_partial_offload_info()`.

Important details:
- The callback flag model preserves binary compatibility: new optional callbacks require new `MC_*` bits.
- VLAN ID zero is translated to `MAC_VLAN_UNTAGGED` at the provider boundary to disambiguate untagged traffic from priority-tagged VLAN 0.
- Ring classification distinguishes no/software/hardware/passthrough classification and determines whether MAC must classify incoming traffic.
- Private APIs at the bottom expose packet header/offload metadata and explicitly note synchronization requirements with the userspace `mac_test` program.

Relevance to subset A: Not filesystem code, but it is core OS/network kernel infrastructure in the included illumos tree.
