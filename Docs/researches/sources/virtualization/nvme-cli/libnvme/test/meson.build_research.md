# File Research: sources/virtualization/nvme-cli/libnvme/test/meson.build

## Role

`test/meson.build` is the main Meson test orchestration file for libnvme’s test directory. It defines developer executables, unit tests, conditional feature tests, and subdirectories.

## Behavior

It runs Python-based public symbol and public header checks when Python is available. It builds hardware-oriented developer executables such as `main-test`, plus unit-test executables for C++, registers, ZNS, MI, MCTP, UUID, topology tree, fabrics helpers, utility helpers, PSK helpers, and headers.

Conditional blocks depend on build options and detected libraries: C++ compiler availability, `want_mi`, `want_fabrics`, `NVME_HAVE_NETDB`, `json_c_dep`, and `openssl_dep`.

For `mock-ifaddrs`, it builds a preloadable library and sets `LD_PRELOAD` plus `ASAN_OPTIONS=verify_asan_link_order=0` for tests needing deterministic interface enumeration.

It enters `subdir('ioctl')`, optionally `subdir('nbft')`, and, when JSON-C is present, `subdir('sysfs')` and `subdir('config')`.

The final loop generates one self-sufficiency test per public `<nvme/*.h>` header from `test-header.c.in`.

## Dependencies

- Meson build variables from the parent project: dependencies, feature flags, generated link args, and header list.
- Test sources in this directory and subdirectories.

## Filesystem/Storage Relevance

This file describes how libnvme validates its storage-management API surface across ioctl, MI, fabrics, sysfs topology, NBFT discovery, and header compatibility.
