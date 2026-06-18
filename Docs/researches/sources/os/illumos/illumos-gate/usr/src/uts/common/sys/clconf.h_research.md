# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/clconf.h

This header defines cluster boot configuration access basics. It declares `nodeid_t`, reserves node id zero as `NODEID_UNKNOWN`, and documents that valid node ids run from 1 to `clconf_maximum_nodeid()`.

Kernel exports initialize cluster configuration and fetch current/maximum node ids.
