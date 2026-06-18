# File Research: sources/virtualization/spdk/module/bdev/gpt/gpt.h

## Purpose
Defines the GPT module's internal data model, constants, GUIDs, parse phases, and parser prototypes.

## Main Contents
The header defines the current SPDK GPT partition type GUID, the deprecated old GUID that preserves an off-by-one sizing behavior, a 32 KiB GPT read buffer size, GUID comparison macro, parse-phase enum, and `struct spdk_gpt` fields for buffer state, LBA geometry, parsed header, and partition entries.

## Dependencies
Includes SPDK GPT spec and logging headers.

## Risks and Notes
`REGISTER_GUID_DEPRECATION` conditionally registers the old GUID deprecation in exactly one compilation unit. Consumers of `struct spdk_gpt` must set `parse_phase`, buffer, sector size, and total sector fields before parsing.
