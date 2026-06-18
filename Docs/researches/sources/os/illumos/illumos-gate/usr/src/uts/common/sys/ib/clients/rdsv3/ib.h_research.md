# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rdsv3/ib.h

This OFED-derived RDSv3 InfiniBand transport header defines the RDSv3-over-IB connection, device, send/receive ring, ACK, credit, MR, and statistics interfaces.

Core definitions:
- Defaults cover FMR size/pool, max SGE, receive SGE count, send/receive WR counts, retry count, supported minor protocols, max receive allocation, and CQ poll size.
- Page fragments represent fixed `RDSV3_FRAG_SIZE` receive fragments with DMA mapping metadata.
- `rdsv3_ib_incoming` wraps generic incoming messages with IB fragment lists and pool/device ownership.
- `rdsv3_ib_connect_private` is versioned CM private data containing addresses, protocol version/mask, ACK sequence, and credit.
- Send/receive work records tie messages/RDMA ops/fragments to work rings.
- `rdsv3_ib_work_ring` tracks alloc/free positions and counters plus an empty wait queue.
- `rdsv3_ib_connection` stores CM ID, PD, MR, CQs, send and receive rings, soft-CQ threads, receive assembly state, ACK state, flow-control credits, batching counters, and receive allocation limit.
- `rdsv3_ib_device` stores per-HCA IPs, connections, OFED device/PD, fragment/incoming/FMR pools, limits, HCA attributes, soft-CQ workers, IBT HCA handle, and AF group.
- Stats cover connection races, CQ/tasklet activity, TX/RX ring pressure, credits, ACKs, and MR pool behavior.

Risk-sensitive invariants:
- Credit packing assumes `atomic_t` is at least 32 bits.
- ACK work requests use magic WR ID `~0ULL`; sends set high bit `RDSV3_IB_SEND_OP`.
- Device connection lists are protected by either global nodev lock or per-device spinlock.
