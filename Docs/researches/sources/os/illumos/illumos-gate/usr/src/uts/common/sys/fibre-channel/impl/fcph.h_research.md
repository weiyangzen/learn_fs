# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/impl/fcph.h

Defines low-level FC-PH frame constants and the Fibre Channel frame header layout. It covers `r_ctl` routing/info masks and values, FC type values for link services and device data, `F_CTL` bits, `DF_CTL` bits, and well-known fabric addresses.

`FC_WELL_KNOWN_ADDR(x)` recognizes the well-known range plus domain-controller IDs. `fc_frame_hdr_t` models the 24-byte FC frame header using endian-dependent bitfields for D_ID, S_ID, F_CTL/type, sequence fields, OX_ID/RX_ID, and relative offset.

This header underpins every `fc_packet_t` command/response frame header and is a protocol ABI within the Fibre Channel stack.
