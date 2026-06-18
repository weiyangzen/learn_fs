# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/iser/iser_ib.h

## Purpose

Defines iSER's InfiniBand transport state and IBT-facing routines: HCA inventory, queue pair sizing/depth tracking, RC channel state, address conversion/path lookup, channel allocation/open/close, receive posting, CQ handlers, and async handler entry points.

## Main Definitions

- External globals: `iser_state` and `iser_taskq`.
- `iser_hca_t`: list node, failure flag, IBT client/HCA/PD handles, HCA attributes, GUID, port info, and per-HCA message/data memory pools and kmem caches.
- Receive queue low-water percentage, receive-post batching limit, and send-CQ poll limit.
- Queue sizing constants:
  - 64-bit kernels use larger receive queue default than 32-bit kernels.
  - Send queue size is 2000.
  - SGL size is 1.
  - Default IRD/ORD values.
- `iser_qp_t`: QP lock, SQ/RQ sizes, RQ depth/current level/min post level/low-water mark, and pending taskq flag.
- `iser_chan_t`: RC channel lock, IBT channel handle, local/remote IP and ports, IBT path info, HCA pointer, send/recv CQs and sizes, QP tracking, SQ post lock/count/max count, and back-pointer to iSER connection.
- Prototypes for IB init/fini, service register/bind/unbind/deregister, sockaddr/IBT address conversion, path lookup, channel allocation with or without path lookup, RC channel open/close/free, receive posting, CQ handlers, and IB async handling.

## Integration Notes

`iser_chan_t` is the IB transport object referenced by `iser_conn_t`. It owns the IBT channel/CQs and tracks both RQ refill pressure and SQ outstanding posts.

## Risks and Gotchas

- Receive queue sizes are intentionally below power-of-two boundaries so HCA drivers can round up while leaving headroom.
- 32-bit kernels use much smaller receive queues due to memory pressure.
- RQ refill uses low-water and taskq-pending state; double scheduling must be avoided.
