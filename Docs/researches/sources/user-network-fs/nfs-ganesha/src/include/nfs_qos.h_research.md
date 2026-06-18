# sources/user-network-fs/nfs-ganesha/src/include/nfs_qos.h

## Purpose

`nfs_qos.h` declares optional QoS support for NFS I/O throttling. When `ENABLE_QOS` is set, it defines bandwidth, IOPS, and token accounting for per-export, per-client, or per-export-per-client classes.

## Important APIs, Types, and Functions

Flags mark QoS I/O, read bypass, compound I/O, and IOPS accounting. Defaults and bounds cover bandwidth, IOPS, tokens, and refresh intervals. Types include `qos_status_t`, `qos_class_type_t`, `qos_op_type_t`, `qos_op_cb_arg`, `timer_entry_t`, `qos_client_entry_t`, `qos_bucket_t`, `qos_block_config_t`, and `qos_class_t`. APIs include class insertion/free/copy, client lookup, BW/IOPS drainers, read/write/compound callbacks, `qos_process`, `qos_process_iops`, `qos_init`, and `shutdown_qos`.

## Control Flow

NFSv4 read/write/compound processing calls QoS functions with size, op type, compound data, and DS flag. QoS buckets account bandwidth/IOPS/tokens, enqueue timer entries when limits are exceeded, possibly disable transport receive for token-exhausted clients, and resume callbacks when timers expire or credits refresh.

## State and Persistence Behavior

QoS state is in memory: global config, export/client classes, per-bucket counters, wait queues, token renewal timestamps, locks, metrics handles, and suspended transport state. It does not persist across restart, but it directly delays client I/O.

## Dependencies and Integration Points

It depends on Ganesha lists, pthreads, compound data, exports/clients, SVCXPRT, config blocks, and optional metrics. Integration points are NFSv4 read/write, export/client managers, config reload, DBus QoS manager, and monitoring.

## Risks and Test Signals

Risks include deadlocks around bucket/class locks, failed wakeups for queued I/O, incorrect combined read/write accounting, transport receive left disabled, token refresh overflow, config bounds errors, and high-cardinality metrics. Tests should enable each QoS mode, throttle read/write/compound IOPS, verify callbacks resume, reload config, exhaust tokens, drain queues on shutdown, and compare metrics/counters with observed throughput.
