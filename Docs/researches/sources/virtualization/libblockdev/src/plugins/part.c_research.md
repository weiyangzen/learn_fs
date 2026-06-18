# File Research: sources/virtualization/libblockdev/src/plugins/part.c

## Purpose

Implements the partition-table plugin using libfdisk. It supports MBR and GPT table creation, queries, partition creation/deletion/resizing, and selected partition metadata updates.

## Main Responsibilities

- Manage `BDPartSpec` and `BDPartDiskSpec` copy/free lifecycle.
- Open libfdisk contexts and write/reread labels.
- Create MBR or GPT partition tables.
- Query disk, partition, free-space, and best-fit free-region metadata.
- Create normal, extended, and logical partitions with alignment handling.
- Delete and resize partitions.
- Set GPT names, type GUIDs, UUIDs, and attributes.
- Set MBR partition IDs and bootable flags.
- Convert table/type enums to string identifiers.

## Important Helpers

- `get_part_num()` extracts the numeric suffix from a partition path, including paths ending in digit-separated `pN` style.
- `fdisk_ask_callback()` routes libfdisk info/warning prompts to libblockdev logging.
- `get_device_context()` creates, assigns, configures, and returns a libfdisk context.
- `close_context()` deassigns and unreferences a context.
- `write_label()` writes the in-memory disklabel, optionally locks the device with `flock()`, and asks the kernel to reread either changed partitions or the whole table.
- `get_part_type_guid_and_gpt_flags()` reads GPT type GUID, type name, and attributes for a partition.
- `get_part_spec_fdisk()` converts a libfdisk partition into `BDPartSpec`.
- `get_disk_parts()` returns partitions and/or free regions, adding synthetic metadata regions where libfdisk does not expose parted-style metadata areas.
- `get_max_part_size()` computes maximum resize size using partition/free-space ordering.

## Important Public Functions

- `bd_part_init()` initializes the C locale and records libfdisk version.
- `bd_part_is_tech_avail()` reports MBR and GPT as supported.
- `bd_part_create_table()` creates a new `dos` or `gpt` disklabel.
- `bd_part_get_part_spec()`, `bd_part_get_part_by_pos()`, `bd_part_get_disk_spec()`, `bd_part_get_disk_parts()`, and `bd_part_get_disk_free_regions()` provide query APIs.
- `bd_part_get_best_free_region()` selects the best region for normal, logical, or extended partition creation.
- `bd_part_create_part()` creates a partition, auto-selecting type for `BD_PART_TYPE_REQ_NEXT`.
- `bd_part_delete_part()` removes a partition.
- `bd_part_resize_part()` changes a partition size, with alignment and max-size handling.
- `bd_part_set_part_name()`, `bd_part_set_part_type()`, `bd_part_set_part_id()`, `bd_part_set_part_uuid()`, `bd_part_set_part_bootable()`, and `bd_part_set_part_attributes()` update partition metadata.
- `bd_part_get_part_table_type_str()` and `bd_part_get_type_str()` return stable string names.

## Dependencies and Interactions

- Uses libfdisk for table parsing, manipulation, alignment, partition typing, and kernel reread operations.
- Uses libblockdev utility progress/log APIs around mutating operations.
- Uses a dedicated C locale for stable `strerror_l()` text.
- Uses Linux/macros from the build environment, including `MiB` constants in size calculations.

## Notable Details

- GPT supports only normal partitions in `bd_part_create_part()`.
- MBR auto-selection creates logical partitions inside existing extended partitions; with three primary partitions it can create a new extended partition first, then create a logical partition inside it.
- For libfdisk versions before 2.36.1, creating a new extended partition forces a full partition-table reread.
- Resize-to-maximum has libfdisk-version-specific handling for default end alignment.
- Requested growth slightly beyond max size is clamped when the excess is within 4 MiB; larger excess is rejected.
- `bd_part_get_type_str()` expects enum-style single-bit values or zero; mixed flag values can map by integer log2 rather than by full flag composition.
