# File Research: sources/virtualization/open-iscsi/usr/flashnode.c

Builds netlink/iovec parameter payloads for firmware flashnode configuration and prints flashnode summaries.

Main responsibilities:
- `flashnode_info_print_flat` prints transport, flashnode index, portal address/port, TPGT, and target name.
- Typed encoders allocate netlink attributes for ISID, IPv4/IPv6 addresses, uint8/uint16/uint32 values, and fixed-size strings.
- `flashnode_build_config` walks user-requested parameter names and appends matching encoded flashnode attributes to the outgoing iovec array.

Supported settings include:
- Session enable/disable, discovery session flags, immediate data, InitialR2T, ordering, CHAP, bidi CHAP, ERL, timing, burst sizes, target name/alias, TPGT, discovery parent metadata, portal type, and CHAP indexes.
- Connection portal address/port, max recv/xmit lengths, digest flags, SNACK, TCP timestamp/Nagle/window scale/timer settings, fragmentation, keepalive, redirect IP, segment size, local port, IPv4 TOS, IPv6 traffic class/flow label/link-local address, TCP WSF, StatSN and ExpStatSN.

Notable details:
- `to_key` formats connection-indexed idbm field names using index `0`, matching `ISCSI_CONN_MAX == 1`.
- IPv4 vs IPv6 address encoding is selected by `sess.portal_type`.
- Default connection port is 3260 if unset.
