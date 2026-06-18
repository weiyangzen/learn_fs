# File Research: sources/virtualization/libblockdev/src/plugins/smart/drivedb-parser.c

## Purpose

Parses compiled-in smartmontools drive database entries to map SMART attribute IDs to model-specific attribute names.

## Main Responsibilities

- Free arrays of `DriveDBAttr` records.
- Provide a no-op lookup when `drivedb.h` is unavailable.
- When `drivedb.h` is available, include the generated known-drives table.
- Parse `-v` preset definitions from drive database records.
- Match drive model and optional firmware regexes.
- Return a NULL-terminated array of SMART attribute ID/name mappings.

## Important Functions

- `free_drivedb_attrs()` frees each attribute name, each record, and the array.
- `parse_attribute_def()` parses smartmontools-style `id,format[+],name[,HDD|SSD]` attribute definitions and ignores definitions without an attribute ID.
- `parse_presets_str()` scans option-style preset strings and records parsed `-v` attribute definitions in a hash table.
- `drivedb_lookup_drive()` builds defaults when requested, overlays drive-specific presets for matching model/firmware entries, and converts the hash table to a `DriveDBAttr **`.

## Dependencies and Interactions

- Includes `smart.h` and `smart-private.h` for `DriveDBAttr`.
- Uses GLib regex and hash table APIs.
- Uses `bd_utils_log_format()` for debug logging on invalid regexes.
- The compiled-in `builtin_knowndrives` array is populated by including `<drivedb.h>` when `HAVE_DRIVEDB_H` is defined.

## Notable Details

- Entries with model families `VERSION`, `USB`, and `DEFAULT` are skipped during drive-specific matching; `DEFAULT` is handled separately when requested.
- Attribute definitions are keyed by numeric ID, so later matching presets replace earlier/default names.
- The firmware regex path compiles the firmware regex but matches it against `model`, not `fw`, which is a notable behavior to verify if firmware-specific presets matter.
- Returned attribute order follows hash-table iteration order, not numeric ID order.
