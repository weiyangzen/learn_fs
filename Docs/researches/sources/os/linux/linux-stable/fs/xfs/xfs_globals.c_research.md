# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_globals.c

## Purpose

Defines global XFS tunable parameters and debug/runtime global settings.

## Main Contents

- `xfs_params`, containing tunable parameter ranges and defaults:
  - panic mask
  - error level
  - sync daemon timer
  - stats clear
  - inheritance flags
  - rotor step
  - filestream timer
  - blockgc timer
- `xfs_globals`, containing:
  - log recovery delay
  - mount delay
  - assert behavior
  - debug pwork thread setting
  - debug log attribute replay toggle
  - btree bulk-load leaf and node slack defaults

## Important Notes

- Timer units are centiseconds except `blockgc_timer`, which is seconds.
- `xfs_params` exists even without sysctl support because other XFS code reads these values.
- Btree bulk-load slack defaults of `-1` mean use the default 75% fill behavior.

## Research Notes

This is a configuration state file, not an algorithmic component. Its values influence behavior across mount, error handling, allocation policy, background cleanup, and debug/testing paths.
