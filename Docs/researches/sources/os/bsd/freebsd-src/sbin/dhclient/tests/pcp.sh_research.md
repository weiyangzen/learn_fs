# File Research: sources/os/bsd/freebsd-src/sbin/dhclient/tests/pcp.sh

## Purpose
ATF integration tests for dhclient against an ISC DHCP server in virtual networking setups, including PCP/VLAN priority handling.

## Main Elements
- `generic_dhcp_cleanup()`: kills dhclient/dhcpd, removes generated files, and runs `vnet_cleanup`.
- `normal` test: creates an epair and jail, runs DHCP server on server side, runs dhclient in jail, and checks assigned address.
- `pcp` test: loads netgraph modules, creates VLAN/eiface path for VLAN 0 tagged frames, sets PCP on jail interface, runs DHCP server through netgraph interface, and verifies dhclient receives the expected address.
- `pcp_cleanup()`: shuts down netgraph nodes and removes cleanup list.
- `atf_init_test_cases()`: registers both tests.

## Dependencies And Integration
Uses FreeBSD ATF, `vnet.subr`, jails, epair interfaces, `dhcpd` from `isc-dhcp44-server`, netgraph modules, `ngctl`, and `ifconfig`.

## Risk Notes
Requires root, external DHCP server package, and exclusive network resources. Cleanup assumes pid files exist and may fail noisily if setup aborts before they are created.
