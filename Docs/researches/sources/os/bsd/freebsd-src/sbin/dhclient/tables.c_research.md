# File Research: sources/os/bsd/freebsd-src/sbin/dhclient/tables.c

## Purpose
Defines DHCP option metadata, default outbound option priority, and universe lookup initialization.

## Main Elements
- `dhcp_universe`: global DHCP option namespace.
- `dhcp_options[256]`: maps every option code to name, format string, universe, and numeric code. Known options include standard IP arrays, text fields, DHCP control options, domain-search, classless-routes, and placeholders for undefined codes.
- `dhcp_option_default_priority_list[]`: preferred emission order for outbound options, including mandatory DHCP options, common network options, and undefined-option sweep.
- `sizeof_dhcp_option_default_priority_list`: exported size.
- `universe_hash`: global universe-name hash.
- `initialize_universes()`: creates option-name hash, populates `dhcp_universe.options`, and registers the universe.

## Dependencies And Integration
Used by config parsing, option formatting, option assembly, and script export naming. Format codes are interpreted by `pretty_print_option()` and parser code.

## Risk Notes
Option metadata is central data. A wrong format string can misparse, misformat, or misvalidate network-provided option data.
