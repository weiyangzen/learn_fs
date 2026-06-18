# File Research: sources/virtualization/nvme-cli/libnvme/test/ioctl/meson.build

## Purpose
Meson build/test definitions for ioctl mock tests.

## Behavior
Configures whether the platform has glibc-style `ioctl`, builds `mock-ioctl` from `mock.c` and `util.c`, sets it in `LD_PRELOAD`, configures ASAN preload ordering, and registers test executables for ANA, async, features, identify, logs, zns, misc, and discovery when fabrics is enabled.

## Relevance
Provides the test harness that intercepts ioctl calls so libnvme passthrough APIs can be verified without real NVMe hardware.
