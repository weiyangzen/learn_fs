# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_fc.h

Purpose: Defines the core in-kernel driver data model for Emulex Fibre Channel adapters: packets, nodes, ports, channels, rings, memory pools, SLI3/SLI4 runtime state, HBA state, locking aliases, register access helpers, interrupt dispatch selection, and endian swap helpers.

Key definitions:
- `emlxs_buf_t`: per-I/O packet wrapper linking `fc_packet_t`, port, node, channel, IOCB, XRI, timeouts, abort state, LUN, DID, packet flags, and optional FCT/SAN diagnostic state.
- Packet flags model queue residency, completion state, timeout/flush/abort, swapped payloads, response validity, allocation, and stale/valid state.
- `emlxs_vpd_t`: persistent adapter/VPD identity and firmware version data.
- `emlxs_queue_t`: generic first/last/count/max queue structure.
- `emlxs_buf_info_t` / `MBUF_INFO`: allocation/DMA mapping descriptor.
- `emlxs_channel_t`: abstraction for SLI3 rings or SLI4 WQ/CQ I/O paths with response deferral, locks, timeout, and counters.
- `emlxs_ring_t`: SLI2/3 command/response ring state.
- `emlxs_node_t` / `NODELIST`: discovered remote node state, WWNs, DID, RPI/XRI, service parameters, per-channel transmit queues, optional DH-CHAP/SAN diagnostic/throttle state.
- `emlxs_memseg_t`: memory pool segment descriptor with high/low-water and dynamic growth metadata.
- `emlxs_stats_t`: broad HBA statistics for link, mailbox, IOCB, FCP, ELS, CT, IP, unsolicited buffers, resets, and optional FCT.
- Optional target-mode support defines FCT states, counters, and efficient power-of-two bucket macros for target I/O size statistics.
- `emlxs_port_t`: per-physical/virtual port state, VPI object, mode flags, WWNs, service parameters, D_IDs, ALPA data, node table, packet polling locks, ULP callbacks, unsolicited buffers, optional FCT and SAN diagnostic state.
- SLI access macros map SLI3 CSR/SLIM and SLI4 BAR registers through DDI accessors.
- `emlxs_sli3_t`: SLI3 SLIM/HBQ/register/ring/BPL state.
- `emlxs_sli4_t`: SLI4 BARs, doorbells, extents, FCF/VFI/RPI/XRI tables, queues, dump region, SLI parameters, and port identity.
- `emlxs_sli_api_t`: function-pointer table abstracting SLI3 vs SLI4 operations.
- `emlxs_hba_t`: top-level adapter object covering PCI identity, DMA attributes, VPD, link state, memory pools, service parameters, adapter state/flags, SLI union, I/O completion, channels, iotags, mailbox, interrupts, timers, GPIO, power management, ioctl, events, config, kstats, logging, ports, optional DH-CHAP/firmware/dump state, and reset state.

Dependencies and interactions:
- Includes `emlxs_fcf.h`, so FCF/VFI/VPI/RPI/XRI state is embedded into the port/HBA model.
- Uses illumos kernel primitives, Leadville FCA types, COMSTAR FCT types under `SFCT_SUPPORT`, and many hardware protocol types from `emlxs_hw.h`.
- Extern function prototypes that operate on these structures are in `emlxs_extern.h`.

Implementation notes:
- Lock alias macros such as `EMLXS_PORT_LOCK`, `EMLXS_MBOX_LOCK`, `EMLXS_TX_CHANNEL_LOCK`, and `EMLXS_FCF_LOCK` encode locking conventions for implementation files.
- `EMLXS_STATE_CHANGE` and `_LOCKED` update adapter state and set hardware-error flags on `FC_ERROR`.
- `MODSYM_SUPPORT` optionally routes Leadville/COMSTAR calls through dynamically resolved function pointers.
- Endian macros provide unconditional swaps and conditional LE/BE swaps; note the `LE_SWAP24_*` definitions reference `X` before being overridden for one modrev case.
