# File Research: sources/os/bsd/freebsd-src/sbin/ifconfig/ifgroup.c

`ifgroup.c` adds ifconfig support for interface groups. It registers `group` and `-group` commands, an `af_group` status callback, and the global `-g groupname` option for listing group members.

Core behavior is ioctl driven: `setifgroup()` uses `SIOCAIFGROUP`, `unsetifgroup()` uses `SIOCDIFGROUP`, and `printgroup()` uses `SIOCGIFGMEMB`. Group names are rejected if they end in a digit and are bounded by `IFNAMSIZ`.

Status output uses `ifconfig_get_groups(lifh, ctx->ifname, &ifgr)` and prints all groups except the implicit `all` group. `printgroup()` opens an `AF_LOCAL` datagram socket, first queries required buffer length, then allocates and fetches membership.

Dependencies include `<net/if.h>`, `libifconfig`, and the shared `ifconfig.h` command registration system. Memory ownership is straightforward: `ifgr.ifgr_groups` is freed after status/list use.

Notable edge behavior: duplicate group add is not fatal (`EEXIST` ignored), missing group removal is not fatal (`ENOENT` ignored), and `printgroup()` exits the process after printing because it is a top-level option callback.
