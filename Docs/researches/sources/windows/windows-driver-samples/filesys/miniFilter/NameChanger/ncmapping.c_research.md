# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/NameChanger/ncmapping.c

## Purpose

`ncmapping.c` builds, initializes, validates, and tears down runtime mapping structures. A mapping path stores multiple `UNICODE_STRING` views over one allocated full-path buffer: full path, volume path, parent path, final component, and volume-less path.

## Functions

- `NcIsMappingPathZeroed`, `NcInitMappingPath`, and `NcTeardownMappingPath` manage a single `NC_MAPPING_PATH`.
- `NcBuildMappingPath` combines a volume name, mapping parent path, and final component into one full path allocation. It sets all string slices and counts backslash components in volume and full path for later overlap tests.
- `NcBuildMappingPathFromVolume` queries a `PFLT_VOLUME` name with `FltGetVolumeName` and builds a mapping path from that volume plus configured parent/final strings.
- `NcBuildMappingPathFromFile` queries a parent `FILE_OBJECT` name, chooses opened or normalized form, parses it, then builds the mapping path with a supplied final component.
- `NcIsMappingEntryZeroed`, `NcInitMappingEntry`, and `NcTeardownMappingEntry` manage long/short path pairs. Teardown avoids double-freeing when long and short entries share the same buffer.
- `NcIsMappingZeroed`, `NcInitMapping`, `NcTeardownMapping`, and `NcBuildMapping` manage a complete real/user mapping pair. `NcBuildMapping` builds the real normalized path, aliases real short to real long, then builds user short opened and user long normalized paths.

## Integration

The component counts and string slices built here are consumed by `NcComparePath`, name generation, create redirection, directory enumeration, notification merging, file information rewriting, and FSCTL result rewriting.

## Risks and Notes

The implementation relies on ownership invariants: each `NC_MAPPING_PATH.FullPath.Buffer` owns the allocation, and other fields are slices. Accidental independent freeing of slice fields would be invalid. Real long and short paths can intentionally alias the same buffer.
