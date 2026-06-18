# File Research: sources/virtualization/libblockdev/src/plugins/mdraid.h

## Role
Public header for the MD RAID plugin.

## Constants and Errors
- Defines empirically chosen defaults for MD superblock and chunk size.
- Defines `BDMDError` values for unavailable tech, command failure, parse failure, bad format, no match, and invalid input.

## Public Structs
- `BDMDExamineData` describes metadata found on an MD member: device, RAID level, member count, name, size, array UUID, update time, member UUID, events, metadata version, and chunk size.
- `BDMDDetailData` describes an active array: device, metadata, creation time, level, name, size values, device counts, clean state, UUID, and container.

## API Surface
Declares lifecycle, availability, superblock-size calculation, create/destroy/activate/deactivate/run, incremental nominate/denominate, add/remove member, examine/detail, UUID conversion, node/name lookup, status, bitmap get/set, and sync-action request functions.
