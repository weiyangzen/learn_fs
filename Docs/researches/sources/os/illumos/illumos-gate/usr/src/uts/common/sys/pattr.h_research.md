# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pattr.h

## Purpose
Defines packet attribute types and payload structures for link-layer address/SAP metadata, hardware checksum offload metadata, large-send offload flagging, and zerocopy metadata.

## Main Interfaces
- Attribute type constants:
  - `PATTR_DSTADDRSAP`
  - `PATTR_SRCADDRSAP`
  - `PATTR_HCKSUM`
  - `PATTR_ZCOPY`
- `pattr_addr_t`: physical address plus group-address flag and address length.
- `pattr_hcksum_t`: checksum start/stuff/end offsets, checksum value union, and checksum/offload flags.
- Checksum flags:
  - `HCK_IPV4_HDRCKSUM`
  - `HCK_IPV4_HDRCKSUM_OK`
  - `HCK_PARTIALCKSUM`
  - `HCK_FULLCKSUM`
  - `HCK_FULLCKSUM_OK`
  - `HCK_FLAGS`
  - `HCK_TX_FLAGS`
- LSO flags:
  - `HW_LSO`
  - `HW_LSO_FLAGS`
- `pattr_zcopy_t`: zerocopy flags wrapper.

## Dependencies And Relationships
No explicit includes in the file; it assumes common fixed-width and kernel typedefs are available from includers. These attributes are used by networking code to attach metadata to packet paths.

## Research Notes
Several flag values are intentionally reused for transmit and receive meanings, for example `HCK_IPV4_HDRCKSUM` versus `HCK_IPV4_HDRCKSUM_OK`.
