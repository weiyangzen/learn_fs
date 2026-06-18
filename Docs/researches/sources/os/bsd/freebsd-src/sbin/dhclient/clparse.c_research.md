# File Research: sources/os/bsd/freebsd-src/sbin/dhclient/clparse.c

## Purpose
Parses `dhclient.conf` and lease files into client configuration, interface state, options, and lease lists.

## Main Elements
- `read_client_conf()`: initializes option universes and top-level defaults, reads config statements if the config file exists, and ensures the active interface has client/config structures.
- `read_client_leases()`: reads lease file entries and stops on corruption.
- `parse_client_statement()`: handles send/default/supersede/prepend/append options, media, hardware, request/require/ignore lists, timers, VLAN PCP, script, interface blocks, leases, aliases, and reject lists.
- `parse_X()`: parses hex byte sequences or strings.
- `parse_option_list()`: parses comma-separated option names.
- `parse_interface_declaration()`: applies nested config to a named real or dummy interface.
- `interface_or_dummy()`, `make_client_state()`, `make_client_config()`: manage real/dummy interface configuration objects.
- `parse_client_lease_statement()` / `parse_client_lease_declaration()`: parse leases, associate with interfaces, maintain active and historical lease lists.
- `parse_option_decl()`: parses option values according to option format strings into `option_data`.
- `parse_string_list()` and `parse_reject_statement()`: parse media lists and rejected server address lists.

## Dependencies And Integration
Uses lexer functions from `conflex.c`, token definitions from `dhctoken.h`, DHCP option tables/universes, and dhclient global interface/time state.

## Risk Notes
Option data is accumulated in a fixed 1024-byte hunk buffer with explicit overflow checks. Lease ordering matters: the last lease for an interface becomes active unless superseded/expired.
