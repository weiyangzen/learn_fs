# File Research: sources/os/bsd/freebsd-src/sbin/route/Makefile

Purpose: FreeBSD build definition for the `route` utility.

Behavior:
- Builds `PROG=route` with `route.c` and generated `keywords.h`.
- Adds `-DINET` and `-DINET6` depending on build options.
- Adds `route_netlink.c` unless netlink support is disabled; otherwise defines `WITHOUT_NETLINK`.
- Adds jail support and `libjail` when enabled and not in rescue builds.
- Enables tests via `SUBDIR.${MK_TESTS}+= tests`.
- Generates `keywords.h` from the `keywords` file using `awk`.

Integration: controls whether `route.c` uses the netlink backend or legacy routing-socket backend. The generated keyword table is included directly by `route.c`.

Risk notes: feature set depends on FreeBSD build options; command behavior changes notably with `MK_NETLINK_SUPPORT`.
