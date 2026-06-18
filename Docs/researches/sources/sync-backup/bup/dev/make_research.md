# sources/sync-backup/bup/dev/make

## Purpose
Wrapper that re-executes the GNU make binary recorded during configuration.

## Important APIs, Types, and Functions
Reads `config/config.var/make` and `exec`s that command with all original arguments.

## Control Flow
If the recorded file cannot be read, prints a message asking the user to run GNU make first and exits 2. Otherwise replaces the process with the configured make.

## State and Persistence Behavior
Reads configure/build state only.

## Dependencies and Integration Points
Used by dev scripts such as doc-branch updates to ensure the same make implementation is used.

## Risks and Test Signals
Risk is stale or missing `config/config.var/make`. Signal is successful exec or clear exit 2.
