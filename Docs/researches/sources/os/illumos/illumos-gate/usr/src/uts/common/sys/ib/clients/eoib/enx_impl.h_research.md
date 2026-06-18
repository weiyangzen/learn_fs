# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/eoib/enx_impl.h

## Purpose

Defines the private implementation surface for the EoIB nexus driver (`eibnx`), which discovers EoIB gateways through FIP solicitation/advertisement, manages per-HCA-port monitor threads, tracks gateway state, and creates/configures `eoib` child nodes.

## Main Definitions

- Nexus return codes, debug flags/macros, default log size, monitor/node-creator thread names, and default unicast solicitation period.
- HCA/port inventory structures: `eibnx_port_t` and `eibnx_hca_t`.
- Port-monitor WQE sizing for solicitation/advertisement handling and CQ size.
- WQE type/flag constants and `eibnx_wqe_t` containing type, buffer size, SGL, IBT WR, lock, and state flags.
- TX/RX descriptors with MR handles, lkeys, and fixed WQE arrays.
- `eibnx_gw_addr_t`: address vector, GID, QPN, QKey, and P_Key for discovered gateways.
- Gateway state constants and `eibnx_gw_info_t`: advertisement status, address, GUIDs, keepalive periods, control QPN, LID, port ID, vNIC counts, flags, SL/RSS count, and gateway strings.
- Gateway packet type enum and message wrapper.
- Child-node tracking with devinfo pointer, gateway pointer, and node name.
- Port-monitor event bitmasks, multicast group status flags, and `eibnx_thr_info_t` for one HCA port monitor.
- Node-creation queue entries and bus configuration flags.
- `eibnx_t`: nexus global/per-instance state with IBT handle, HCA list, monitor list, node queue thread state, and bus operation state.
- Event tags delivered to child EoIB instances.
- Prototypes for monitor/event handlers, IBT setup/rollback, FIP solicit/parse, WQE queue helpers, gateway/child list management, logging, node creation/configuration, bus operations, devctl entry points, and globals.

## Integration Notes

The nexus sits above IBT and below child `eoib` instances. It joins well-known FIP multicast groups, discovers gateways, prepares devinfo properties/events, and handles gateway login ACK packets that may arrive at the nexus due to gateway behavior documented in `eib.h`.

## Risks and Gotchas

- Send WQEs for unicast solicitations are preallocated during receive processing constraints; acquisition cannot always sleep.
- Gateway liveness has separate unavailable/available/ready-to-login states plus advertisement heartbeat flags.
- Bus operation flags are partly protected by `nx_busop_lock` and partly by the in-progress bit itself.
- Child node creation is asynchronous through a node queue thread.
