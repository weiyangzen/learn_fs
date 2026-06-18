# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/1394/adapters/hci1394_extern.h

This is the common extern declaration header for global `hci1394` symbols.

Exported globals:
- `hci1394_statep`: driver soft-state anchor defined in `hci1394.c`.
- `hci1394_evts`: HAL event vector defined in `hci1394_s1394if.c`.
- `hci1394_split_timeout`, `hci1394_addr_map[]`, `hci1394_phy_delay_uS`, and `hci1394_phy_stabilization_delay_uS`: configuration/address-map globals defined in `hci1394_extern.c`.

It includes `h1394.h` and `adapters/hci1394.h`, so consumers get the services-layer types and the aggregate adapter definitions required to interpret these globals.
