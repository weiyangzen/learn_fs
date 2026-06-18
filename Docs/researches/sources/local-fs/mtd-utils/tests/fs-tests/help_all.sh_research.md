# File Research: sources/local-fs/mtd-utils/tests/fs-tests/help_all.sh

## Purpose
Convenience script to print help output for filesystem tests.

## Key Elements
Runs `-h` on selected simple tests, stress atoms, and `integrity/integck`, separating each invocation with a line of dashes.

## Dependencies
Requires `/bin/sh` and built test binaries at the relative paths used by the script.

## Behavior/Risks
Assumes it is run from `tests/fs-tests`; it has no error handling if binaries are missing or not executable.
