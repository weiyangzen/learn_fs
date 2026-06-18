# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/hwconf.h

## Role

`hwconf.h` defines structures and kernel functions for parsed hardware configuration data, driver binding tables, parent lists, and minor-node permissions.

## Key Interfaces and Data

- `MAX_HWC_LINESIZE` is 1024.
- `hwc_class` links class exporters and class names.
- `hwc_spec` describes prototype device nodes: parent name, class name, device name, system properties, hash linkage, and major number.
- `par_list` groups prototype child specs by parent major for sorted parent loading.
- `bind` maps names to binding names and numeric IDs.
- `mperm_t` stores minor-name permissions: mode, uid, gid, and userland-only driver/owner/group strings.
- Kernel globals `mb_hashtab` and `sb_hashtab` are binding hash tables.
- Kernel functions parse hardware config, create/free/delete parent lists, map parent lists to major numbers, get child specs for a devinfo/major, and free spec lists.

## Dependencies and Use

The header includes DDI type and property definitions. Several fields differ under `_KERNEL` versus userland to support name-based permission parsing outside the kernel.

## Research Notes

This is boot/configuration infrastructure, not device runtime I/O. It models parsed config file state before or during device tree construction.
