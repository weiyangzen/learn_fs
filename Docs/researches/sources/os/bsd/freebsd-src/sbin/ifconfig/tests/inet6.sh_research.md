# File Research: sources/os/bsd/freebsd-src/sbin/ifconfig/tests/inet6.sh

`inet6.sh` is an ATF shell test file for IPv6-specific ifconfig behavior. It sources the shared VNET helper and defines `netmask`, `broadcast`, and `delete6` test cases.

`netmask` validates bug 286910 coverage: using IPv4-style `netmask` with an IPv6 address must fail with `ifconfig: netmask: invalid option for inet6`, while CIDR `/64` succeeds and displays `prefixlen 64`. It also checks the invalid option is rejected during address removal syntax.

`broadcast` similarly verifies that `broadcast` is rejected for IPv6 add and remove forms with the expected error message.

`delete6` adds `fe80::42/64` to an epair, verifies the scoped address is visible, removes it with `inet6 -alias`, and verifies it no longer appears.

All tests require root and use VNET/epair isolation. Cleanup for each case calls `vnet_cleanup`.
