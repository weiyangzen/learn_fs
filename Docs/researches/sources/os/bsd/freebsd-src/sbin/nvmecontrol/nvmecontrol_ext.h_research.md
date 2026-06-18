# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/nvmecontrol_ext.h

Purpose: Minimal extension header exposing controller-printing functionality.

Key contents:
- Declares `void nvme_print_controller(struct nvme_controller_data *cdata);`.

Dependencies:
- Expects `struct nvme_controller_data` to be visible to includers, typically via NVMe headers.

Research notes:
- This is a small interface file, likely used where full internal `nvmecontrol.h` is not desired.
