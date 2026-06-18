# File Research: sources/os/linux/linux-stable/fs/efivarfs/vars.c

## Summary
Wraps EFI variable runtime operations and validates sensitive variable formats.

## Main Responsibilities
- Validates boot-order, load-option, device-path, uint16, and ASCII-string variables.
- Converts EFI UTF-16 names plus GUIDs to efivarfs filenames.
- Iterates firmware variables at mount/resync time.
- Deletes, sizes, reads, and writes EFI variables under the efivar lock.

## Key APIs
- `efivar_get_utf8name()`
- `efivar_validate()`
- `efivar_variable_is_removable()`
- `efivar_init()`
- `efivar_entry_delete()`
- `efivar_entry_size()`
- `efivar_entry_get()`
- `efivar_entry_set_get_size()`

## Important Behavior
The validation table is both a format validator and whitelist for variables that are not immutable by default. Duplicate firmware variables during enumeration trigger a warning and terminate enumeration to avoid infinite loops.

## Risks
Firmware behavior is not trusted: enumeration size is capped, duplicates are detected, malformed boot variables are rejected, and EFI status codes are converted carefully.
