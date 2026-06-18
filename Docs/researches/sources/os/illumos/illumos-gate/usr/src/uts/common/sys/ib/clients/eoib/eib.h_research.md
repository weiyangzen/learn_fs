# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/eoib/eib.h

## Purpose

Defines public EoIB encapsulation constants, vNIC ID packing helpers, vHUB ID construction, nexus-to-leaf event names and properties, gateway information passed to EoIB instances, and soft interrupt priorities.

## Main Definitions

- EoIB encapsulation header size and bit masks/shifts for signature, version, TCP/IP checksum state, FCS bit, multi-segment bit, segment offset, and segment ID.
- Encapsulation field values for signature/version/checksum states and shortcuts for common TX/RX encapsulation words.
- Driver name `eoib`.
- vNIC/device instance packing constants:
  - 6 bits for Solaris vNIC instance.
  - 9 bits for EoIB pseudo-device instance.
  - Macros to extract and build the combined vNIC ID.
- `EIB_VHUB_ID()` builds a vHUB ID from gateway port ID and VLAN.
- NDI event names for gateway availability, vNIC login acknowledgements, and gateway-info updates.
- Device properties used on EoIB child nodes, including HCA, port, gateway identity, keepalive periods, control QPN, LID, port ID, availability, host-managed vNIC flag, SL, RSS QPN count, names, and vendor ID.
- `eib_gw_info_t`: gateway information delivered by the nexus, with string buffers sized one byte larger than FIP source fields.
- Soft interrupt priorities for data, control, and admin CQ handling.

## Integration Notes

This is shared between the EoIB leaf driver and EoIB nexus driver. It exposes the contract by which `eibnx` creates/configures `eoib` instances and signals gateway/login state.

## Risks and Gotchas

- The 15-bit vNIC ID split caps vNICs at 64 per EoIB device and pseudo-devices at 512; comments note this is a gateway-response workaround.
- Property names are string contracts with devinfo/NDI consumers.
- Encapsulation checksum shortcut constants assume exact bit layout of the 32-bit EoIB header.
