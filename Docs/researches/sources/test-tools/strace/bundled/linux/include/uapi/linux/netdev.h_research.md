# sources/test-tools/strace/bundled/linux/include/uapi/linux/netdev.h

Purpose: auto-generated generic netlink UAPI for the `netdev` family, exposing device XDP features, page pools, NAPI, queue stats, dmabuf bindings, queue leases, and io_uring provider hooks.

Important APIs/types/functions: exports family name/version, feature enums `netdev_xdp_act`, `netdev_xdp_rx_metadata`, `netdev_xsk_flags`, queue/NAPI enums, attribute groups for dev/page-pool/stats/NAPI/queue/qstats/lease/dmabuf, commands such as device get, page-pool get/stats, queue get/create, NAPI set, bind RX/TX, and multicast groups.

Control flow: userspace uses generic netlink to query devices, queues, NAPI instances, page pools, queue stats, bind queues to dmabufs or io_uring, create queues, and receive management/page-pool notifications.

State/persistence behavior: get/stat commands are observational; bind/create/set commands mutate netdev queue, NAPI, dmabuf, lease, and io_uring association state. Stats update with traffic and allocation behavior.

Dependencies/integration: generated from `netdev.yaml`. Integrates with XDP, AF_XDP, NAPI, page_pool, dmabuf, io_uring zcrx, and hardware queue management.

Risks and test signals: generated numeric gaps and nested attributes need exact decoding. Tests should cover feature bitmasks, queue type/scope enums, qstats counters, dmabuf fd/id attributes, bind RX/TX commands, and multicast group names.
