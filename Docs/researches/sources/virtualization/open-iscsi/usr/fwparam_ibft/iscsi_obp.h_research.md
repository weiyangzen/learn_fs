# File Research: sources/virtualization/open-iscsi/usr/fwparam_ibft/iscsi_obp.h

Defines OpenFirmware boot parameter types for the PPC firmware parser.

Contents:
- Device types: none, block, network, iSCSI.
- TFTP/boot qualifiers: bootp, dhcpv6, ipv6, iscsi, ping.
- iSCSI boot parameters: block size, retries, CHAP IDs/passwords, client/server/gateway/DHCP addresses, filename, initiator/target IQNs, target LUN, initiator port, ISID, iSNS/SLP, subnet mask, and timeout.
- `ofw_obp_param` stores a variable-length string value.
- `ofw_dev` stores parsed device path, type, qualifiers, parameter pointers, config partition, device path, and MAC.

It also declares parser callback helpers implemented in `fwparam_ppc.c`.
