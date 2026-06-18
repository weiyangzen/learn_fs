# File Research: sources/local-fs/xfsdump/common/mlog.h

## Role

This header declares the message logging interface, log levels, subsystem selectors, modifier flags, and exit-summary helpers.

## Log Levels And Modifiers

Levels are encoded in the low byte:

- silent/normal
- verbose
- trace
- debug
- nitty

Modifier flags include bare output, NOTE/WARNING/ERROR labels, and no-lock logging.

## Subsystems

The header assigns subsystem IDs and bit-shifted subsystem flags for general, process, drive, media, inventory, dump/restore-specific subsystem, and excluded files.

## Exported State

The logging configuration exposes:

- `mlog_level_ss[]`
- `mlog_showlevel`
- `mlog_showss`
- `mlog_timestamp`
- `mlog_ss_names[]`

These are mutable from the interactive signal dialog.

## API

The header declares staged initialization, stream-count reporting, level override, formatted logging, exit recording/hinting, final exit flush, explicit lock/unlock for dialog integration, and fold-line generation.
