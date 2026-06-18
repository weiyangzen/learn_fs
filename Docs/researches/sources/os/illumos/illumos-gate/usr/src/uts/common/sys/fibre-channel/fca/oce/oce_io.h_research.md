# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/oce/oce_io.h

This header defines the OCE driver's queue object model and hardware I/O operation prototypes. It bridges generic ring buffers and hardware mailbox formats into event, completion, mailbox, transmit, receive, and RSS queue management.

Key contents:
- Mailbox and statistics timeouts.
- Queue length/type/state enums for EQs, CQ callbacks, mailbox queues, WQs, RQs, CQs, and RSS.
- `eq_config` and `oce_eq` for event queues with lock, hardware ID, parent/callback context, ring, refcount, state, and delay/vector configuration.
- `cq_config` and `oce_cq` for completion queues with eventability, DMA coalescing, associated EQ, handler, ring, state, and refcount.
- `mq_config`, `oce_mq`, and `oce_mbx_ctx` for mailbox queue state and asynchronous callback context.
- `wq_config` and `oce_wq` for transmit queues, including TX locks, CQ, ring, descriptor caches, free-list structures, preallocated copy buffers/DMA handles, queue state, WQ ID, and scheduling counters.
- `rq_config`, `rq_shadow_entry`, and `oce_rq` for receive queues, including CQ association, receive buffer descriptor arrays, shadow ring, freelist/recycling indexes, pending/buffer-available counts, queue state, and RX/recycle locks.
- `link_status` structure mirroring relevant common mailbox link-status response fields.
- DMA allocation/free and ring-buffer create/destroy prototypes.
- Queue management prototypes for EQ delay, EQ/CQ arming, EQ draining, and RSS readiness.
- Bootstrap and mailbox posting/waiting/dispatch prototypes.
- Hardware and PCI lifecycle prototypes, network interface create/delete, reset, and TX/RX setup/teardown.
- TX/RX operations for queue selection, WQ/RQ CQ draining, start/clean, packet send, receive discharge, and RX pending wait.
- Mailbox helper prototypes for header initialization and firmware/hardware operations: firmware version, MAC address, interface create/delete, interrupt vectors, link status, RX filters, multicast table, firmware config, stats, flow control, promiscuous mode, MAC add/delete, VLAN config, link config, RSS config, and private mailbox ioctl dispatch.

Dependencies:
- Includes DDI types, mutex, STREAMS, debug, byteorder, `oce_hw.h`, and `oce_buf.h`.
- Depends on descriptor and mailbox structures from `oce_hw.h` and `oce_hw_eth.h`.

Research notes:
- This is the operational API used by the OCE implementation files to create/destroy queues, post mailbox commands, and drive TX/RX.
- Queue state is explicit but simple (`QDELETED`, `QCREATED`); higher-level state is in `oce_impl.h`.
- Receive queue management contains separate locks for RX processing and buffer recycling.
