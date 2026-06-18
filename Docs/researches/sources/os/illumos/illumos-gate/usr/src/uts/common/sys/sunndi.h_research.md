# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sunndi.h

`sunndi.h` defines Sun-specific Nexus Driver Interface operations. It is kernel-only and builds on `sunddi.h`/`esunddi.h` to let nexus drivers create, configure, offline, remove, hotplug, and resource-manage child devinfo nodes.

Return values extend DDI status with NDI-specific errors for no memory, bad handles, copy faults, busy devices, unbound devices, invalid requests, unsupported events, and claimed/unclaimed event delivery.

Property functions provide nexus-owned mutation/removal APIs for boolean, int, int64, string, and byte-array properties. Devinfo lifecycle APIs allocate/free child nodes, lock/unlock/try-enter devinfo nodes, hold/release devinfo and drivers, rename nodes, bind drivers, asynchronously bind persistent nodes, online/offline/config/unconfig children, and perform generic devctl ioctl handling. Flag bits describe removal, attach-on-online, recursive config/unconfig, persistent behavior, PROM naming, event suppression, debug, reprobe, forced online/offline, branch events, detach context, single-threading disable, and user-requested operations.

Devctl convenience functions copy in/out `devctl_iocdata`, extract path/name/address/minor/AP data, return device/AP/bus state, and create devinfo nodes from devctl requests. Bus state getters/setters and child finders support nexus ioctl implementations.

The NDI event framework includes upward event posting, busop event callback registration/removal/cookie lookup, event handles, event definitions/cookies/sets, event attributes, callback list structures, bind/unbind, cookie retrieval, callback add/remove/run/do-one, tag/name conversion helpers, debug dump support, and default bus_config/bus_unconfig helpers.

Hotplug APIs register/unregister connection points, request state changes, and walk connection points. Bus Resource Allocator APIs define allocation request constraints for memory, I/O, PCI bus numbers, prefetchable memory, and interrupts, with map setup/destroy, allocate, and free routines.

Node classification helpers identify PROM, pseudo, persistent, hotplug, and hidden nodes and set/clear hidden state. Fault support defines `DDI:DEVI_FAULT` payload data and access/DMA handle fault mark/clear functions. The end of the file handles driver.conf property merging and NDI "flavor" support for nexus drivers whose children have multiple flavor-specific private-data interpretations.
