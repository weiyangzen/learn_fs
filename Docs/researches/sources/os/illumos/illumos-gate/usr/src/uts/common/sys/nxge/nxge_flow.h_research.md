# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_flow.h

## Purpose
Defines user/kernel flow-specification structures and ioctl payloads for receive classification and hash configuration.

## Main Interfaces
- Flow match structures for TCP/UDP IPv4/IPv6, AH/ESP IPv4/IPv6, raw IP, Ethernet programmable frames, generic IP user classes, and IPv6 fragments.
- `flow_spec_t`: packed entry/mask union keyed by `flow_type`.
- Flow type constants from `FSPEC_TCPIP4` through `FSPEC_HDATA`.
- Conversion macros for IPv4/IPv6 addresses, ports, TCAM class, and protocol fields.
- `flow_resource_t`: packed flow object tying a channel cookie, flow cookie, location, and `flow_spec_t`.
- Receive classification ioctl commands:
  - `NXGE_RX_CLASS_GCHAN`
  - `NXGE_RX_CLASS_GRULE_CNT`
  - `NXGE_RX_CLASS_GRULE`
  - `NXGE_RX_CLASS_GRULE_ALL`
  - `NXGE_RX_CLASS_RULE_DEL`
  - `NXGE_RX_CLASS_RULE_INS`
- `rx_class_cfg_t`: packed ioctl payload with rule count, rule locations, and flow resource.
- RX hash/tunnel config commands:
  - `NXGE_IPTUN_CFG_*`
  - `NXGE_CLS_CFG_*`
- `iptun_cfg_t` and `cfg_cmd_t`: packed tunnel/hash configuration payloads.

## Dependencies And Relationships
Includes `netinet/in.h` and aliases `S6_addr32` for IPv6 address word access. FFLP/classification ioctl handling is declared in `nxge_impl.h` as `nxge_rxclass_ioctl()` and `nxge_rxhash_ioctl()`.

## Research Notes
The packed structs are ABI-facing ioctl payloads; field order and size are part of the interface. `rawip4_spec_t` uses `struct in6_addr` fields for source/destination despite its IPv4 name, so consumers should follow the existing layout rather than inferring from the type name.
