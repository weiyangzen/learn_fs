# File Research: sources/virtualization/libblockdev/src/plugins/mdraid.c

## Role
Implements the libblockdev MD RAID plugin. It wraps `mdadm`, parses `mdadm` output into stable structs, performs MD UUID conversions, resolves MD names/nodes, and uses sysfs for state, bitmap, and sync-action controls.

## Main Dependencies
- GLib for strings, memory, errors, regexes, and hash tables.
- `blockdev/utils.h` for command execution, device resolution, and file writes.
- `bs_size.h` for parsing human-readable chunk sizes from `mdadm`.
- `glob`, `time`, and POSIX access helpers.
- Local dependency checking for `mdadm >= 3.3.2`.

## Public Data Helpers
- Copy/free functions are implemented for `BDMDExamineData` and `BDMDDetailData`.
- `bd_md_error_quark()` defines the plugin error domain.
- `bd_md_init()` is a no-op; `bd_md_close()` clears cached dependency availability.
- `bd_md_is_tech_avail()` gates all MD RAID modes on `mdadm`.

## Parsing Model
- `parse_mdadm_vars()` parses key/value output from both colon-separated human output and equals-separated brief/export output.
- It keeps the first value for duplicate keys and handles migration output containing `<--`.
- `get_examine_data_from_table()` extracts array level, device count, name, array size, array UUID, update time, member UUID, event count, metadata version, and chunk size.
- `get_detail_data_from_table()` extracts detail state such as metadata, creation time, level, name, array size, per-device size, device counts, clean state, UUID, and container.

## Device and Name Resolution
- `get_sysfs_name_from_input()` accepts `/dev/md/<name>`, `/dev/<node>`, node names, or MD names and resolves the sysfs block name.
- `get_mdadm_spec_from_input()` accepts a path/name/node and returns a suitable mdadm operand, validating existing `/dev/...` paths.
- `bd_md_node_from_name()` resolves `/dev/md/<name>` to the underlying block node basename.
- `bd_md_name_from_node()` scans `/dev/md/*` symlinks and resolves each to find the user-facing MD name for a node.

## RAID Operations
- `bd_md_get_superblock_size()` calculates reserved metadata/headroom size, including the mdadm 1.1/1.2 reshape headroom behavior.
- `bd_md_create()` builds `mdadm --create` with level, raid-devices, optional spares, metadata version, bitmap location, chunk size, and disks.
- `bd_md_destroy()` zeroes superblocks.
- `bd_md_deactivate()` stops an array.
- `bd_md_activate()` assembles an array or scans all arrays, supports UUID filtering and degraded start, and treats already-active arrays as success.
- `bd_md_run()` starts a possibly degraded array.
- `bd_md_nominate()` and `bd_md_denominate()` use `mdadm --incremental` to add or fail a device in its appropriate array.
- `bd_md_add()` adds a device and can grow non-redundant arrays by setting `--raid-devices`.
- `bd_md_remove()` optionally fails a resolved member path before removing it.

## Query and Control Operations
- `bd_md_examine()` combines normal, export, and brief `mdadm --examine` outputs to fill stable metadata, canonicalize UUIDs, and discover `/dev/md/...` array paths.
- `bd_md_detail()` parses `mdadm --detail` and `--export`, canonicalizing UUID and recording container information.
- `bd_md_get_status()` reads `/sys/class/block/<md>/md/array_state`.
- `bd_md_set_bitmap_location()` validates bitmap location and runs `mdadm --grow --bitmap`.
- `bd_md_get_bitmap_location()` reads sysfs bitmap location, returning `none` when the bitmap file is absent.
- `bd_md_request_sync_action()` validates and writes one of `resync`, `recovery`, `check`, `repair`, or `idle` to sysfs `sync_action`.

## UUID Handling
- `bd_md_canonicalize_uuid()` converts mdadm UUID form `8:8:8:8 hex` into canonical dashed UUID form.
- `bd_md_get_md_uuid()` performs the reverse conversion.
- Both functions validate with GLib regexes and return `BD_MD_ERROR_BAD_FORMAT` on invalid input.

## Filesystem/Storage Relevance
This file manages Linux software RAID arrays that commonly back filesystems or higher block layers such as LVM. It is both an orchestration wrapper over `mdadm` and a sysfs control path for live array state.
