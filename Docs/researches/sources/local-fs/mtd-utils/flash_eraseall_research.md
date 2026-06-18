# File Research: sources/local-fs/mtd-utils/flash_eraseall

## Purpose
Compatibility wrapper for the removed `flash_eraseall` command.

## Key Elements
Prints a deprecation message, appends `0 0` when arguments are present, and execs `flash_erase`.

## Dependencies
Requires `/bin/sh` and `flash_erase` in `PATH`.

## Behavior/Risks
Maintains old command behavior by erasing from offset 0 to end of device; this is destructive by design.
