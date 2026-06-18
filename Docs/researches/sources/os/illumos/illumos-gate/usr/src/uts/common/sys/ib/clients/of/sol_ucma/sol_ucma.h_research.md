# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/sol_ucma/sol_ucma.h

This Solaris user-CMA driver header defines sol_ucma file, channel, multicast, event, and global driver state.

Core definitions:
- Limits define two supported paths and up to 128 listens.
- Event-file close flags track no close, event in progress, and disabled state.
- `sol_ucma_file_t` embeds a user object and tracks all CM IDs for an open file, poll support, blocking event CVs, pending event list/count, and close coordination.
- `sol_ucma_chan_t` embeds a user object for each RDMA CM ID and tracks file membership, channel/user IDs, event count, underlying `rdma_cm_id`, QP number/handle, QP flush state, listen backlog, and flags.
- `sol_ucma_mcast_t` tracks multicast user objects, UID/ID, owning channel, address, and event count.
- `sol_ucma_event_t` binds an event response to its channel and optional multicast object.
- `sol_ucma_t` stores global driver synchronization, devinfo, open count, LDI/module handles, IB/iWARP client handles, and initialization state.

Risk-sensitive invariants:
- Event delivery requires synchronization between file event lists, poll wakeups, blocking `GET_EVENT`, and close disablement.
- Channel objects tie user-visible IDs to kernel `rdma_cm_id` lifetime.
- QP flush state coordinates UCMA with sol_uverbs when connection teardown must flush user QPs.
