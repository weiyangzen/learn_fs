# File Research: sources/os/bsd/freebsd-src/sbin/route/tests/basic.sh

Purpose: ATF shell tests for basic `route` add/change/delete and interface route behavior.

Test cases:
- `basic_v4`: creates an epair/VNET jail, adds an IPv4 route, verifies gateway, changes it, verifies again, deletes it, and checks absence.
- `basic_v6`: same lifecycle for IPv6 with `-6` and `no_dad`.
- `interface_route_v4`: adds an IPv4 interface route using `-iface`.
- `interface_route_v6`: adds an IPv6 interface route using `-iface`.
- Each test cleans up through `vnet_cleanup`.

Integration: sources `utils.subr` for jail/network helpers such as `vnet_mkepair`, `vnet_mkjail`, `check_route`, and cleanup. Exercises actual `route` command behavior inside a jail.

Risk notes: tests require root, `jail`, and `jq`. They verify gateway presence/value, not full route flags or backend-specific monitor/get output.
