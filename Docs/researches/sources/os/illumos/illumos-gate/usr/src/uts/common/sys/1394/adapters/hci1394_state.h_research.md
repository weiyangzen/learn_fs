# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/1394/adapters/hci1394_state.h

This private header defines the top-level `hci1394` driver soft state.

`struct hci1394_state_s` contains:
- Module handles for OHCI, async, vendor, CSR, and isoch subsystems.
- Services-layer self-ID buffer pointer used across bus reset/self-ID completion.
- Embedded `hci1394_drvinfo_t` with shared driver metadata.
- Adapter vendor information.
- PCI config handle and byte-swap flag.
- `h1394_halinfo_t` passed to the 1394 services layer.

It includes the key private subsystem headers and `h1394.h`. The layout intentionally keeps handles/pointers near the top for debugging. Warlock annotations identify generation and statistics fields modified under single-thread assumptions.
