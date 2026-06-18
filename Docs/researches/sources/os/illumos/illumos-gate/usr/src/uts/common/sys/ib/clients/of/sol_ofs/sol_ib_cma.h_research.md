# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/sol_ofs/sol_ib_cma.h

This transport-specific CMA header holds the InfiniBand-side state used by Solaris RDMA-CM.

Core definitions:
- Defines the global UDP QKey as `RDMA_UDP_QKEY`.
- `ibcma_dev_t` records selected local device information: node GUID, port, pkey index/value, SGID, and IP address.
- Address flags track whether local/remote addresses were set and whether the local address was wildcard.
- `ibcma_chan_t` stores path info, local/remote IBT IP addresses, port, service ID, RC request data, QP modify status, selected device, multicast list, and multicast count.
- `ibcma_mcast_t` records multicast membership context: CMID, caller context, socket address, and multicast GID.

Risk-sensitive invariants:
- `ibcma_chan_t` is embedded in the generic CMA channel union and is the IB transport’s private state.
- Address flags determine whether source/destination binding and wildcard handling are complete.
- Multicast list ownership and count must stay synchronized with join/leave handling.
