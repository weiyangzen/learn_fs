# File Research: sources/virtualization/nvme-cli/libnvme/test/mock-ifaddrs.c

## Role

`mock-ifaddrs.c` provides deterministic replacements for `getifaddrs()` and `freeifaddrs()` for fabrics and topology tests.

## Behavior

`getifaddrs()` allocates four `ifaddrs_storage` entries and returns a linked list with:

- `eth0` IPv4 address `192.168.1.20`.
- `eth0` IPv6 link-local address `fe80::dead:beef`.
- `lo` IPv4 loopback `127.0.0.1`.
- `lo` IPv6 loopback `::1`.

Each entry stores address, netmask, broadcast address, interface name, and flags in one allocation. `freeifaddrs()` frees the allocation starting from the first returned node.

## Dependencies

- Standard networking headers for `ifaddrs`, socket address structures, address families, and interface name sizes.
- Used by Meson through a preloadable shared library.

## Filesystem/Storage Relevance

This supports deterministic NVMe-oF address parsing and topology tests, especially link-local IPv6 scope behavior.
