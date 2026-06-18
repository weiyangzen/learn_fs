# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/exacct_impl.h

## Role

`exacct_impl.h` contains private extended-accounting implementation structures used by libexacct and the kernel to assemble process, task, flow, and network accounting records.

## Error And Usage Structures

- `EXACCT_SET_ERR()` is a no-op in kernel builds and calls `exacct_seterr()` in userland builds.
- `task_usage_t` records task CPU time, fault/message/block/char/context/signal/swap/syscall counts, start/finish times, and ancestor task id.
- `proc_usage_t` records process resource counters, CPU/start/finish times, RSS average/max, pid/user/group/project/task ids, accounting flags, command, controlling tty major/minor, wait status, ancestor pid, zone name, and node name.
- `flow_usage_t` records IPv4/IPv6 addresses, protocol, ports, DS field, byte/packet counts, creation/last-seen times, project, user, address-family flag, and action name.

## Network Records

- Defines network record types `EX_NET_LNDESC_REC`, `EX_NET_FLDESC_REC`, `EX_NET_LNSTAT_REC`, and `EX_NET_FLSTAT_REC`.
- `net_stat_t` holds name, input/output bytes, input/output packets, error counts, and reference flag.
- `net_desc_t` holds names, Ethernet addresses, VLAN/SAP/priority, bandwidth, IP addresses, IPv4 flag, ports, protocol, DS field, and descriptor type.

## Byte Ordering

Declares `exacct_order16()`, `exacct_order32()`, and `exacct_order64()` for exacct record byte-order conversion.
