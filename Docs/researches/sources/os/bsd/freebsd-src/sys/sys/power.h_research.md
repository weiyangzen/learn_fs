# File Research: sources/os/bsd/freebsd-src/sys/sys/power.h

This header defines user and kernel power-management interfaces. User-visible content includes `enum power_transition` for standby, suspend, and hibernate requests, plus `PIOTRANSITION`, an ioctl accepting a `uint32_t` transition selector.

Kernel-only content defines power management provider types, command constants, and `enum power_stype`, which maps high-level transitions to concrete sleep methods such as awake, standby, firmware suspend, suspend-to-idle, firmware hibernate, and poweroff. It provides fixed-length names, a static name table, global sysctl-selected sleep type variables, and conversion helpers between names and sleep types.

Power management providers register with `power_pm_register()` by type, callback, argument, and supported sleep-type set. The header also declares provider type lookup, suspend entry, performance/economy power profile state accessors, and a `power_profile_change` eventhandler. Filesystem relevance is suspend/resume coordination: filesystems and storage stacks must tolerate power state transitions, and userland initiates them through this ABI.
