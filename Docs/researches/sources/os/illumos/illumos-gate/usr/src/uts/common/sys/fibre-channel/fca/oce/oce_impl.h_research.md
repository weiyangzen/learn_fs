# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/oce/oce_impl.h

This is the main private OCE driver implementation header. It gathers illumos DDI/MAC/FMA dependencies, driver defaults, hardware access macros, adapter state, GLDv3 entry points, hardware lifecycle routines, interrupt routines, and fault-management helpers.

Key contents:
- Size constants, device/queue limits, MTU/frame limits, jumbo-frame limits, multicast limit, queue defaults, buffer sizes, interrupt vector defaults, RSS table/key sizes, and DMA alignment.
- Default OCE capability and enable flags for broadcast, untagged, promiscuous, multicast-promiscuous, and L3/L4 pass-through modes.
- FMA capability flags and default RSS/flow-control settings.
- PCI BAR identifiers for device config, CSR, and doorbell regions.
- Register read/write macros over DDI access handles for CSR, doorbell, and device-config mappings.
- PCI function extraction macro using `PCICFG_INTR_CTRL`.
- Driver lock macros and enums for ring size and driver state.
- `struct oce_dev`, the central adapter state:
  - bootstrap mailbox and locks;
  - WQ/RQ/CQ/EQ/MQ arrays;
  - state/suspend/attach progress;
  - TX/RX copy and reclaim thresholds;
  - PCI BAR mappings and MAC handle;
  - kstats and hardware statistics buffer;
  - link status/speed;
  - interrupt handles/capabilities;
  - queue counts and ring sizes;
  - MTU, MAC address, multicast table, RSS/LSO/promisc/flow-control settings;
  - firmware config, interface ID, function/capability fields, firmware version;
  - PCI IDs and logging controls.
- GLDv3/MAC callbacks for start, stop, send, promiscuous, multicast, unicast, capabilities, ioctl, properties, and stats.
- Hardware lifecycle prototypes for start/stop, hardware identification, BDF lookup, hardware init/fini, adapter setup/unsetup.
- FMA prototypes for init/fini, DMA/register flag setup, ereport emission, and handle checking.
- Interrupt setup/teardown/handler registration and enable/disable prototypes.

Dependencies:
- Includes many illumos kernel headers for DDI, MAC, GLDv3, STREAMS, PCI, FMA, and module support.
- Includes `oce_hw.h`, `oce_hw_eth.h`, `oce_io.h`, `oce_buf.h`, `oce_utils.h`, and `oce_version.h`.

Research notes:
- `struct oce_dev` is the shared state object tying together hardware queues, MAC-layer registration, PCI resources, DMA memory, firmware state, statistics, interrupts, and driver configuration.
- The header is private to the OCE driver and forms the integration layer between illumos MAC/DDI/FMA APIs and the hardware/mailbox definitions.
