# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mac_ether.h

## Role

Ethernet MAC plugin header, defining Ethernet media values and kernel Ethernet-specific statistics.

## Structure

Defines `mac_ether_media_t`, covering unknown/none, 10/100/1G modes, 2.5G/5G, 10G, 25G, 40G, 50G, 100G, 200G, and 400G variants. Kernel builds define `MAC_PLUGIN_IDENT_ETHER`, Ethernet stat IDs appended from `MACTYPE_STAT_MIN`, `ETHER_NSTAT`, and `ETHER_STAT_ISACOUNTER()`.

## Dependencies And Consumers

User/kernel code can use media enum values for `MAC_PROP_MEDIA` and `ETHER_STAT_XCVR_INUSE`. Kernel MAC Ethernet plugin and drivers use the stat IDs.

## Important Details

The stat enum explicitly says not to reorder and to append only. Media enum values are public property values, so additions are compatible only when appended and interpreted by matching tooling.

## Research Notes

Read completely: 370 lines, 8882 bytes.
