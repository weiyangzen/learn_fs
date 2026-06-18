# File Research: sources/os/plan9/9front/sys/src/9/port/sdloop.c

`sd` loopback backend that exposes an ordinary file/channel as a storage device.

Key responsibilities:
- Tracks loop controllers by backing path.
- Opens backing paths as read/write channels and derives geometry from channel length.
- Supports optional sector size suffix after `!`; defaults to 512 bytes.
- Parses configured loop devices from `loopdev`.
- Implements `verify`, `online`, `bio`, `rio`, `rctl`, `probew`, `clear`, and top-level control hooks for `SDifc`.
- Uses fake SCSI helpers to translate storage requests to block reads/writes.

Important behavior:
- Geometry changes set `drivechange` and increment `vers`.
- I/O errors `Echange` or errors containing `device is down` clear `u->sectors`.
- Flush-cache SCSI commands are treated as successful no-ops.

Notable risks:
- Controller deletion has the same suspicious linked-list loop update pattern as `sdaoe.c`.
- The backing object must support ordinary read/write at byte offsets.
