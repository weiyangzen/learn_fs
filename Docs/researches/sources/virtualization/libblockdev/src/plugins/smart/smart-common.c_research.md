# File Research: sources/virtualization/libblockdev/src/plugins/smart/smart-common.c

This file contains SMART plugin documentation, the shared SMART error domain, lifecycle glue, and boxed-struct copy/free helpers shared by backend implementations.

The top-level documentation explains two SMART backends:
- `libatasmart`, the default lightweight ATA-only backend.
- `smartmontools`, the heavier backend that shells out to `smartctl --json` and supports more device types, including SCSI/SAS.

The documentation also establishes important API semantics:
- The NVMe plugin should be used for NVMe health reporting.
- Callers should use tech availability queries because backend capabilities differ.
- ATA attributes expose both backend-specific names and libblockdev “well-known” names.
- Attribute interpretation is best-effort because vendors reuse SMART IDs and smartmontools JSON does not expose all formatting context.
- The `extra` argument is mainly meaningful for smartmontools, especially for `--device=` passthrough override.

Implemented functions:
- `bd_smart_error_quark()` returns the shared SMART `GQuark`.
- `bd_smart_init()` is currently a no-op returning `TRUE`.
- `bd_smart_close()` calls backend-specific `_smart_close_plugin()`.
- `bd_smart_ata_attribute_free()` frees an ATA attribute and owned strings.
- `bd_smart_ata_attribute_copy()` shallow-copies the struct then deep-copies owned strings.
- `bd_smart_ata_free()` frees a NULL-terminated ATA attribute vector and the `BDSmartATA`.
- `bd_smart_ata_copy()` shallow-copies scalar fields and deep-copies each attribute.
- `bd_smart_scsi_free()` frees `scsi_ie_string` and the `BDSmartSCSI`.
- `bd_smart_scsi_copy()` shallow-copies scalar fields and deep-copies `scsi_ie_string`.

Research relevance:
- This is the shared ABI/ownership layer for SMART boxed data.
- The copy functions preserve scalar fields exactly and only duplicate pointer-owned members.
- Backend implementations must return structures compatible with these ownership rules.
