# File Research: sources/os/plan9/9front/sys/src/cmd/disk/prep/edit.h

## Purpose
Defines the shared partition editor data model and function prototypes.

## Key Contents
- `Part` holds editor-visible partition metadata: display name, kernel ctl name, logical start/end, optional ctl start/end overrides, and changed flag.
- `Edit` holds the active `Disk`, current kernel ctl partitions, current editable partitions, callback table, unit label, dot/end/unit sizing state, and private command-loop flags.
- `Maxpart` caps the generic editor’s partition arrays at 32 entries.
- Declares the shared command loop, partition list helpers, expression parser, kernel ctl diff writer, and allocation helpers.

## Notes
The header is intentionally callback-oriented so MBR, GPT, and Plan 9 partition table tools can share one interactive editor while preserving their own on-disk formats.
