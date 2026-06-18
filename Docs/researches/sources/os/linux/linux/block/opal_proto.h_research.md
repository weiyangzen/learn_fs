# File Research: sources/os/linux/linux/block/opal_proto.h

Defines constants, enums, packet headers, and discovery feature layouts for TCG OPAL self-encrypting drive protocol support.

Key contents:
- Security protocol identifiers for TCG `SECP`.
- OPAL atom/token encodings and masks for tiny/short/medium/long atoms.
- OPAL UID and method enum indexes used by OPAL command construction.
- OPAL token constants for tables, locking ranges, MBR control, properties, and session/list delimiters.
- Locking-state, parameter, and revert constants.
- Packet structures for com packets, packets, data subpackets, response headers, and stack reset.
- Discovery 0 feature codes and structures for TPer, locking, geometry, enterprise SSC, datastore, single-user, OPAL v1, and OPAL v2 features.

Important structures:
- `struct opal_header` nests OPAL com packet, packet, and data subpacket headers.
- `struct d0_features` is the variable-length discovery descriptor wrapper.
- Feature structs use big-endian fields matching the wire format.

Research relevance:
- This header is protocol schema, not behavior.
- It supports block-layer OPAL management code elsewhere by providing wire-compatible layouts and symbolic constants.
