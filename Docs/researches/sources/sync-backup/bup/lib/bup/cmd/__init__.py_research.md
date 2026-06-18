# sources/sync-backup/bup/lib/bup/cmd/__init__.py

## Purpose
Empty initializer for bup command modules.

## Important APIs, Types, and Functions
No code, exports, or runtime symbols.

## Control Flow
No executable control flow.

## State and Persistence Behavior
No state or persistence.

## Dependencies and Integration Points
Allows modules under `bup.cmd` to be imported by the command dispatcher.

## Risks and Test Signals
Risk is command package import failure if packaging changes. Signal is successful import of command modules such as `bup.cmd.bloom`.
