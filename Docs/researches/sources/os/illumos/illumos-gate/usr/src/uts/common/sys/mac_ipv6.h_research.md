# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mac_ipv6.h

## Role

Identifier header for the IPv6 tunneling MAC plugin.

## Structure

Defines `MAC_PLUGIN_IDENT_IPV6` as `"mac_ipv6"` inside the standard guard and C linkage wrapper.

## Dependencies And Consumers

No includes. Consumed by IPv6 tunnel MAC plugin registration and code that refers to the plugin identity.

## Important Details

The header is deliberately minimal and pairs with shared implementation declarations from `mac_ipv4_impl.h`.

## Research Notes

Read completely: 43 lines, 1153 bytes.
