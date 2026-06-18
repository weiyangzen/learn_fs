# sources/sync-backup/casync/src/caformat-util.c

## Purpose
Provides utility conversions for casync archive/index format constants and feature flags. It maps record type IDs to names, parses and formats `--with=` feature names, normalizes feature masks, determines timestamp granularity, maps filesystem attributes to feature bits, derives likely supported features from filesystem magic, and converts digest feature flags.

## Important APIs, Types, and Functions
`ca_format_type_name` names `CA_FORMAT_*` record types. `with_feature_map` backs `ca_with_feature_flags_parse_one` and `ca_with_feature_flags_format`. `ca_feature_flags_normalize`, `ca_feature_flags_are_normalized`, and `ca_feature_flags_normalize_mask` enforce canonical masks. Attribute conversion functions cover Linux chattr flags and FAT attrs. `ca_feature_flags_from_magic` maps FAT, ext, XFS, btrfs, tmpfs, FUSE, and default filesystems to supported metadata. Digest helpers map `CA_FORMAT_SHA512_256` to/from `CaDigestType`.

## Control Flow
Most functions are straight-line table scans or switch statements. Normalization removes redundant mutually exclusive bits: 32-bit UIDs supersede 16-bit, finer time granularity supersedes coarser options, ACL supersedes permissions/read-only, exclude-nodump removes stored nodump, and read-only subvolume implies subvolume.

## State and Persistence Behavior
No mutable state is stored. The output feature mask directly affects persisted archive/index headers and cache compatibility, so canonicalization is part of the on-disk contract.

## Dependencies and Integration Points
Depends on Linux `fs.h` and `msdos_fs.h`, `caformat.h`, `cadigest.h`, and utility helpers. Called by encoder, index reader/writer, FUSE warning code, and option parsing paths.

## Risks
Feature-mask mistakes can create archives that decoders reject or interpret with different metadata semantics. Filesystem magic support is heuristic, especially for FUSE. Formatting uses aggregate names like `best`, `unix`, and `all`, so consumers must understand that the formatted string may not be a minimal list of primitive bits.

## Test Signals
Round-trip parse/format for named features, rejection of unknown bits, normalization idempotence, time granularity selection, chattr/FAT conversions, digest type mapping, and representative filesystem magic cases are the useful tests.
