# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/eoib/fip.h

## Purpose

Defines EoIB FIP wire protocol constants and packed descriptor/message structures for solicitation, gateway advertisement, vNIC login/login ACK/logout-related data, keepalive, vHUB table, and vHUB update messages.

## Main Definitions

- Fixed lengths for vendor IDs, GUIDs, gateway system/port names, multicast GID prefix, vNIC name, and vHUB ID.
- EoIB admin P_Key, FIP/data QKeys, advertise/solicit multicast GUID prefixes.
- FIP protocol version and EoIB opcode/subcodes.
- Basic header flags for gateway availability and solicited messages.
- `fip_proto_t` and `fip_basic_hdr_t`.
- InfiniBand address descriptor with masks for QPN, port ID, and SL.
- Solicitation message: protocol version, basic header, and IB address descriptor.
- Gateway information, gateway identifier, and keepalive descriptors.
- Advertisement message combining IB address, gateway info, gateway ID, and keepalive parameters.
- vNIC login descriptor with MTU, vNIC ID, VLAN/flags, MAC, multicast GID prefix, RSS/MAC multicast counts, syndrome/control QPN, and vNIC name.
- Masks and syndrome codes for vNIC login success/failure.
- Partition descriptor and login/login-ACK message structures.
- vNIC identity descriptor and keepalive message.
- vHUB table entry format and entry type/valid/RSS/QPN/SL masks.
- vHUB update and vHUB table descriptors, including eport state, VP flag, vHUB ID, TUSN, table-size, chunk header flags, and trailing checksum convention.
- vHUB update/table packet wrappers.

## Integration Notes

This is a wire-format header used by both `eoib` and `eibnx`. Parsing/building code must apply endian conversion where appropriate; the structures describe protocol layout and constants but do not enforce conversion.

## Risks and Gotchas

- Some descriptors are variable length or have trailing entries/checksum after the fixed struct; bounds checks must live in parser code.
- Login descriptor bitfields are represented as masks over integer fields, not C bitfields.
- vHUB table fragmentation uses FIRST/MIDDLE/LAST/ONLY flags and TUSN/checksum state; partial table handling is external.
