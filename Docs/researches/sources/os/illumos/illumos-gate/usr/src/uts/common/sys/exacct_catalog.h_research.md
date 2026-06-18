# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/exacct_catalog.h

## Role

`exacct_catalog.h` defines the default SunOS extended-accounting catalog tag layout and default data IDs. Each exacct object begins with a 32-bit catalog tag partitioned into type, catalog, and id fields.

## Tag Layout

- Type occupies bits 31-28 and is masked by `EXT_TYPE_MASK`.
- Types include `EXT_NONE`, unsigned integers of 8/16/32/64 bits, `EXT_DOUBLE`, `EXT_STRING`, `EXT_EXACCT_OBJECT`, `EXT_RAW`, and `EXT_GROUP`.
- Catalog occupies bits 27-24 and is masked by `EXC_CATALOG_MASK`.
- `EXC_NONE`/`EXC_DEFAULT` identify default catalog entries, while `EXC_LOCAL` reserves ids for application-defined local use.
- Data id occupies the low 24 bits and is masked by `EXD_DATA_MASK`.

## Default Data IDs

- Global header ids cover version, file type, creator, hostname, and group header.
- Group ids cover process, task, LWP, tags, partial records, task intervals, flow, RFMA/FMA, and network link/flow descriptors and stats.
- Process ids cover pid, uid/gid, task/project, host/command, start/finish times, CPU times, tty, faults, messages, blocks, chars, context switches, signals, swaps, syscalls, flags, tag, ancestor pid, wait status, zone name, and RSS average/max.
- Task ids cover task/project, host, timing, CPU, resource counters, tag, ancestor task, and zone name.
- Flow ids cover IPv4/IPv6 source/destination, ports, protocol, DS field, byte/packet counts, create/last-seen time, project, uid, and action name.
- FMA ids cover label/version, OS/platform, time, nvlist, device major/minor, inode, offset, and UUID.
- Network descriptor/stat ids cover link/flow identity, Ethernet endpoints, VLAN, SAP, priority, bandwidth, IP/ports/protocol/DS field, current time, bytes, packets, and error packets.
