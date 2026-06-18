# File Research: sources/virtualization/libblockdev/src/lib/plugins.h

## Role
Public plugin metadata header.

## API
- Defines `BDPlugin`, the canonical plugin enum. Ordering is significant because `blockdev.c.in` keeps multiple arrays aligned to it.
- Plugin values include LVM, Btrfs, swap, loop, crypto, multipath, device mapper, mdraid, s390, partitioning, filesystem, nvdimm, nvme, smart, and `BD_PLUGIN_UNDEF`.
- Defines boxed type macro `BD_TYPE_PLUGIN_SPEC`.
- Defines `BDPluginSpec` with:
  - `name`, a `BDPlugin`;
  - `so_name`, optional shared-object name override.
- Declares constructors/copy/free helpers and plugin query functions.

## Dependencies and Interactions
- Consumed by `blockdev.h`, `plugins.c`, and `blockdev.c.in`.
- Any enum change must be reflected in the default soname array, plugin state array, and plugin-name array in `blockdev.c.in`.

## Filesystem/Storage Relevance
This header defines the plugin identity surface used to enable storage-specific modules. Btrfs is represented by `BD_PLUGIN_BTRFS`, filesystem operations by `BD_PLUGIN_FS`, and other block/storage subsystems by their own enum values.
