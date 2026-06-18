# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mac_ipv4.h

## Role

Identifier header for the IPv4 tunneling MAC plugin.

## Structure

Defines `MAC_PLUGIN_IDENT_IPV4` as `"mac_ipv4"` inside the standard guard and C linkage wrapper.

## Dependencies And Consumers

No includes. Consumed by IPv4 tunnel MAC plugin registration and code that refers to the plugin identity.

## Important Details

The header intentionally contains only the plugin identifier; operational helper prototypes live in `mac_ipv4_impl.h`.

## Research Notes

Read completely: 43 lines, 1153 bytes.
