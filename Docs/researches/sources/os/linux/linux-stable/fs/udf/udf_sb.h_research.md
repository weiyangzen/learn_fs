# File Research: sources/os/linux/linux-stable/fs/udf/udf_sb.h

## Summary
Defines UDF superblock state, mount/runtime flags, partition-map state, metadata/sparing/VAT structures, and flag helpers.

## Main Responsibilities
- Sets supported read/write UDF revisions and mount feature flags.
- Defines partition flags and partition map type constants.
- Represents metadata, sparing, virtual, bitmap, and generic partition map state.
- Defines `struct udf_sb_info` for all mounted UDF instance state.
- Provides `UDF_SB()`, `UDF_QUERY_FLAG()`, `UDF_SET_FLAG()`, and `UDF_CLEAR_FLAG()`.

## Important Behavior
`UDF_MAX_READ_VERSION` accepts up to `0x0260` for broken media even though UDF 2.60 should report lower. `UDF_MAX_WRITE_VERSION` is `0x0201`, so newer write-required media becomes read-only.

## Risks
`UDF_FLAG_RW_INCOMPAT` controls whether write mounts are allowed after mount-time feature detection. Partition-specific unions require consumers to check map type and flags before dereferencing.
