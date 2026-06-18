# File Research: sources/os/plan9/9front/sys/src/cmd/cdfs/dat.h

Shared data model and constants for the CD/DVD/BD file server.

Key definitions:
- Media constants for track counts, CD/DVD/BD block sizes, SCSI peripheral types, MMC media types, track types, writability classes, and tri-state flags.
- MMC mode-page offsets and bits for capabilities, write parameters, track modes, data block types, session formats, cache controls, and close-track/session commands.
- `Msf` stores minute/second/frame positions.
- `Track` stores discovered track size, block size, block range, type, MSF boundaries, name, mode, and mtime.
- `Otrack` represents an open track with drive pointer, mode, buffer, change generation, and refcount.
- `Dev` is a method table for drive operations: open, create, read, write, close, TOC refresh, fixate, control, and speed control.
- `Drive` embeds `QLock` and `Scsi` plus media state, tracks, speed information, and device operation table.
- `Buf` stores block-buffering state around an `Otrack`.

Dependencies:
- Requires Plan 9 `Scsi`, `QLock`, and disk/libc types from including compilation units.

Research notes:
- `Drive` is the core cross-file object shared by the 9P server and MMC command layer.
