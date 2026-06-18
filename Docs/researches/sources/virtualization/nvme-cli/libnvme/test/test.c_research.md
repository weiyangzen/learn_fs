# File Research: sources/virtualization/nvme-cli/libnvme/test/test.c

## Role

`test.c` is a hardware-facing exploratory libnvme test program. Unlike the unit tests, it scans real topology and issues many admin commands to discovered controllers and namespaces.

## Behavior

The program creates a libnvme context, scans topology with a subsystem NQN filter, prints discovered hosts/subsystems/controllers, optionally scans one named controller, walks the full topology, and prints namespace identity information including LBA size/count, EUI64, NGUID, UUID, CSI, and path ANA state.

`test_ctrl()` issues identify controller, SMART log, allocated/active namespace lists, controller lists, primary/secondary controller identify, namespace granularity, UUID list, sanitize/reservation/ANA/endurance/telemetry/self-test/command-effects/changed-namespace/firmware/error logs, and many get-features commands. It prints whether each command succeeded.

`test_namespace()` identifies a namespace, computes active LBA format, prints size information, issues identify allocated namespace, identify namespace descriptors, and write-protect feature queries.

The program is not registered as a Meson unit test because it requires real NVMe hardware and meaningful user inspection of output.

## Dependencies

- Public libnvme topology, controller, namespace, and command APIs.
- Internal `nvme/private.h`.
- CCAN endian helpers.
- Real sysfs/NVMe device access for meaningful execution.

## Filesystem/Storage Relevance

This is a broad NVMe storage-device smoke test. It exercises topology scanning and admin/log/feature commands that describe block namespace properties used by higher storage layers.
