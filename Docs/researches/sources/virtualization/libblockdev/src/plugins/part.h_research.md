# File Research: sources/virtualization/libblockdev/src/plugins/part.h

## Purpose

Public API header for the libblockdev partition plugin.

## Main API Surface

- Error domain:
  - `bd_part_error_quark()`
  - `BDPartError`
- Partition table types:
  - MBR/DOS,
  - GPT,
  - undefined.
- Partition type flags:
  - normal,
  - logical,
  - extended,
  - freespace,
  - metadata,
  - protected.
- Requested creation types:
  - normal,
  - logical,
  - extended,
  - next/auto.
- Alignment modes:
  - none,
  - minimal,
  - optimal.
- Data structs:
  - `BDPartSpec`
  - `BDPartDiskSpec`
- Technology categories and modes for MBR/GPT create, modify, and query operations.

## Important Functions Declared

- Lifecycle and availability:
  - `bd_part_init()`
  - `bd_part_close()`
  - `bd_part_is_tech_avail()`
- Table and query operations:
  - `bd_part_create_table()`
  - `bd_part_get_part_spec()`
  - `bd_part_get_part_by_pos()`
  - `bd_part_get_disk_spec()`
  - `bd_part_get_disk_parts()`
  - `bd_part_get_disk_free_regions()`
  - `bd_part_get_best_free_region()`
- Mutation operations:
  - `bd_part_create_part()`
  - `bd_part_delete_part()`
  - `bd_part_resize_part()`
  - metadata setters for name, type, ID, bootable flag, GPT attributes, and UUID.
- String conversion:
  - `bd_part_get_part_table_type_str()`
  - `bd_part_get_type_str()`

## Dependencies and Interactions

- Depends only on GLib at the public header level.
- Implemented by `part.c` using libfdisk.
