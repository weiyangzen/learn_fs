# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mac_6to4.h

## Role

Identifier header for the 6to4 tunneling MAC plugin.

## Structure

Includes `sys/mac_ipv4.h` and defines `MAC_PLUGIN_IDENT_6TO4` as `"mac_6to4"`.

## Dependencies And Consumers

Consumers are MAC plugin registration code and tunnel code that need the plugin identity. It shares IPv4 plugin helpers through the included IPv4 header.

## Important Details

No kernel guard is used around the identifier, so the plugin name is visible to all C consumers.

## Research Notes

Read completely: 45 lines, 1180 bytes.
