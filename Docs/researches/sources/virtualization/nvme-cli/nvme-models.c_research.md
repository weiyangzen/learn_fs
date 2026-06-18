# File Research: sources/virtualization/nvme-cli/nvme-models.c

This file resolves a Linux NVMe controller device name such as `nvme0` into a human-readable PCI product/model description. It reads controller identity values from sysfs, parses a `pci.ids` database, and formats the best available vendor/device/class description.

Public API:
- `nvme_product_name(const char *devname)`: accepts either a bare device name or a path with a final `nvme%d` component, extracts the controller index, and returns a newly allocated product string or `NULL`.

Main flow:
- `nvme_product_name()` strips any leading path with `strrchr()`, validates the final component with `sscanf("nvme%d")`, then delegates to `__nvme_product_name()`.
- `__nvme_product_name()` opens `pci.ids`, builds sysfs paths for `/sys/class/nvme/nvme%d/device/{subsystem_vendor,subsystem_device,vendor,device,class}`, reads those values, scans `pci.ids`, and formats a result string.
- `open_pci_ids()` prefers `PCI_IDS_PATH` when set, otherwise searches common distro locations: `/usr/share/hwdata/pci.ids`, `/usr/share/pci.ids`, and `/usr/share/misc/pci.ids`.
- `parse_vendor_device()` walks indented `pci.ids` device and subsystem-device entries after a vendor match.
- `pull_class_info()` finds class, subclass, and programming-interface descriptions.
- `format_all()` and `format_and_print()` combine class, vendor, device, and subsystem matches into a single display string, falling back to `"Unknown device"`.

Important helpers:
- `read_sys_node()` opens and reads one sysfs attribute, strips a trailing newline, and reports non-ENOENT open errors.
- `is_top_level_match()`, `is_mid_level_match()`, `is_inner_sub_vendev()`, and `is_final_match()` encode the expected indentation and field layout of `pci.ids`.
- `locate_info()` skips numeric fields in matched `pci.ids` lines to return the human-readable text.
- `free_all()` releases static parse-result strings after each lookup.

State and ownership:
- Uses static path buffers and static parse-result pointers for intermediate state.
- The returned product string is heap allocated; callers must free it.
- The implementation is not thread-safe because intermediate parse state is global.

Risk notes:
- Parsing is tightly coupled to `pci.ids` indentation and field widths.
- Several match helpers use fixed-offset `memcmp()` calls, so malformed or unexpectedly short lines could be risky.
- `read_sys_node()` does not explicitly handle `read()` returning `-1` before indexing the buffer, which is a robustness hazard.
- Missing sysfs data, missing `pci.ids`, or an invalid `PCI_IDS_PATH` returns `NULL` or a fallback display string depending on where lookup fails.
- This file is Linux/sysfs-specific and should not be treated as portable device-model discovery code.
