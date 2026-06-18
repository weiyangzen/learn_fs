# sources/test-tools/stress-ng/stress-netdev.c

## Purpose
`stress-netdev.c` implements the `netdev` stressor, which repeatedly enumerates network interfaces and exercises Linux netdevice `ioctl(2)` queries. It is intended to cover interface configuration query paths and some invalid `SIOCGIFCONF` and `SIOCGIFNAME` cases without making persistent network configuration changes.

## Important APIs, Types, and Functions
The exported `stress_netdev_info` registers `stress_netdev()` as a `CLASS_NETWORK` stressor with always-on verification. The helper `stress_netdev_check()` centralizes ioctl error handling and treats common unsupported or permission-related errors as non-fatal. The `STRESS_NETDEV_CHECK` macro passes ioctl names into that helper for diagnostics. The stressor uses `struct ifconf`, `struct ifreq`, `socket(AF_INET, SOCK_DGRAM, 0)`, and many `SIOC*` netdevice commands guarded by compile-time feature macros.

## Control Flow
The stressor opens an IPv4 datagram socket, synchronizes with other workers, and enters a loop while the run continues and no fatal ioctl error has occurred. It first calls `SIOCGIFCONF` with a zeroed `ifconf` to discover the required buffer length, derives the interface count, allocates the buffer, and calls `SIOCGIFCONF` again to fill it. For each interface, it optionally checks the interface index, resolves names, validates returned index behavior, and queries flags, extended flags, address, netmask, metric, MTU, hardware address, hardware map, transmit queue length, destination address, broadcast address, memory, and link information where available. It also sends intentionally malformed `SIOCGIFCONF` lengths and random interface indexes to probe error paths. Each completed pass increments the bogo counter.

## State and Persistence
The only persistent kernel object is the transient socket, closed before return. Interface buffers are allocated and freed inside each loop iteration. The stressor does not set interface flags or addresses; mutation-oriented ioctls are present only in disabled `#if 0` blocks. It stores no durable state and reports failure state through the return code and stress-ng logging.

## Dependencies and Integration Points
This is Linux-specific and requires `SIOCGIFCONF`, `struct ifconf`, and `struct ifreq`. It includes `linux/sockios.h` and `net/if.h` where available. It uses stress-ng shims for memset, memory-free messages, logging, synchronization, process states, bogo counters, and random values. Unsupported builds export `stress_unimplemented` with an explanatory reason.

## Risks
The first `SIOCGIFCONF` call relies on platform behavior that returns the needed length when `ifc_buf` is null; that is Linux-oriented and guarded accordingly. Interface count is computed from `ifc_len / sizeof(struct ifreq)`, which is conventional for this ioctl but not a universal portable interface enumeration strategy. Network namespaces or systems with no interfaces cause skip-like behavior. The `SIOCGIFNAME` validation sets `ifr_ifindex = i`, but Linux interface indexes are not generally dense from zero, so the failure message can be noisy or misleading on systems where the enumerated position does not equal the kernel ifindex.

## Test Signals
Run `--netdev 1 --timeout 1 --verify` on Linux with normal and restricted privileges. Check that lack of optional ioctls is tolerated, at least loopback is discovered, and fatal errors are limited to unexpected ioctl failures. Build tests should cover systems without the required netdevice headers to confirm the unimplemented metadata path.
