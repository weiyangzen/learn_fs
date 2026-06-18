# File Research: sources/os/bsd/dragonflybsd/sys/sys/sockio.h

This header defines socket and network-interface ioctl command numbers.

Key responsibilities:
- Defines generic socket ioctls:
  - high/low water mark get/set
  - OOB mark query
  - process group get/set
- Defines multicast routing counter ioctls:
  - `SIOCGETVIFCNT`
  - `SIOCGETSGCNT`
- Defines interface address, destination, broadcast, netmask, flags, config, metric, alias, capability, index, data, name, description, multicast, MTU, physical/media/generic/status/link address ioctls.
- Defines gif/tunnel physical address ioctls.
- Defines Linux-private compatibility query slots.
- Defines clone interface ioctls:
  - get cloners
  - create/destroy
  - create2
- Defines driver-specific parameter ioctls.
- Defines deprecated polling CPU ioctls.
- Defines TSO length ioctls.
- Defines interface group ioctls.
- Defines extended media query ioctl.

Important invariants:
- Many ioctl numeric slots are preserved with comments for ABI compatibility.
- `SIOCSDRVSPEC` and `SIOCGDRVSPEC` intentionally share command number 123 with different directions.
- Deprecated poll CPU ioctls remain defined for compatibility.

Research notes:
- This is a stable networking control-plane ABI header; structures referenced are defined by networking headers such as `if.h`.
