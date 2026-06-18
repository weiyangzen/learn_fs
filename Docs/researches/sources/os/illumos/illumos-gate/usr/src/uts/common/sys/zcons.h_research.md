# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/zcons.h

`zcons.h` defines constants for the zone console driver. It names the global-zone manager side minor node as `globalconsole` and the non-global-zone subsidiary side minor node as `zoneconsole`. The subsidiary name is chosen so global-zone tools see a meaningful device name, while links inside the zone present it as `console`.

`ZC_IOC` is the base for zone-console ioctls. `ZC_HOLDSUBSID` and `ZC_RELEASESUBSID` instruct the manager side to hold or release a reference to the subsidiary vnode. The comments explain why zoneadmd uses these around console device-node lifetime: holding the subsidiary preserves the STREAMS anchor and `ptem` module even if `ttymon` inside the zone pops STREAMS modules, maintaining terminal semantics while the zone is running.

This file is tightly coupled to the `uts/common/io/zcons.c` implementation and zoneadmd console setup/teardown sequencing.
