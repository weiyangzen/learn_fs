# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mac_ib.h

## Role

InfiniBand/IPoIB MAC plugin header for kernel-only plugin identity, limits, and soft header metadata.

## Structure

Under `_KERNEL`, defines `MAC_PLUGIN_IDENT_IB`, SAP/ethertype/GID constants, `ib_addrs_t`, `ib_header_info_t`, and accessor aliases for destination/source/GRH fields.

## Dependencies And Consumers

Consumers are IPoIB/MAC plugin implementation files that already provide `ipoib_mac_t`, `ipoib_pgrh_t`, and `ipoib_hdr_t` definitions.

## Important Details

The comment explains the "soft" header: IB does not provide a normal link-layer header path compatible with GLDv3, so this structure carries destination/source metadata needed by the MAC layer.

## Research Notes

Read completely: 76 lines, 2064 bytes.
