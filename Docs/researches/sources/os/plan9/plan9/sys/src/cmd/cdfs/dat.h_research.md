# File Research: sources/os/plan9/plan9/sys/src/cmd/cdfs/dat.h

This header defines the `cdfs` media model, drive abstraction, constants, and buffer state.

Key contents:
- Media constants for CD/DVD/BD block sizes, maximum tracks, read transfer sizing, feature map size, and MMC/SCSI type codes.
- Disc/track type enums, writability classes, tri-state flags, MMC mode-page offsets, write parameter bits, close-session functions, TOC formats, write types, track modes, data block types, cache-control bits, and drive capability bits.
- Structs:
  - `Msf`: minute/second/frame address.
  - `Track`: per-track size, block size, block ranges, type, MSF range, exported name/mode/mtime.
  - `Otrack`: open track state, drive pointer, change generation, mode, buffer, and server refcount.
  - `Dev`: drive operation vector for open/create/read/write/close/toc/fixate/control/speed.
  - `Drive`: locked SCSI-backed device plus media type, track table, capability flags, speed state, feature bitmap, and driver auxiliary data.
  - `Buf`: buffered I/O state used by `buf.c`.

Important details:
- `Drive` embeds `Scsi` and a `Dev` operation vector, so MMC code installs methods directly on discovered drives.
- `Readblock` limits CD reads to fit remote 9P RPC behavior.
- The `Drive` state separates drive capability, current disc type, and writable/recordable/erasable properties.

Filesystem relevance:
- Direct. This is the central data definition header for the `cdfs` filesystem service.
