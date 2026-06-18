# File Research: sources/os/plan9/9front/sys/src/cmd/cdfs/mmc.c

MMC/SCSI optical drive backend for `cdfs`, supporting CD/DVD/BD probing, reading, writing, blanking, speed setting, and fixation.

Key behavior:
- Builds SCSI CDBs for mode sense/select, inquiry, start unit, read TOC, read disc/track info, read disc structure, read/write, reserve track, close track/session, synchronize cache, blank, format, and speed control.
- `mmcprobe` validates an MMC device, learns capabilities, caches write-parameter mode page 5 when available, configures cache behavior, and fills the drive method table.
- `mmcgettoc` handles media-change detection, blank-disc probing, disc type inference, DVD/BD structure reads, writeability flags, track discovery, and TOC-derived MSF data.
- `mmctrackinfo` reads per-track metadata, determines audio/data/blank type, computes block ranges/sizes, and tracks next writable address.
- `mmcinfertracks` infers track ends from successive TOC entries for non-writing drives.
- `mmcopenrd` opens a read track and creates a block buffer.
- `mmcread` reads sectors using `READ CD` for non-data CD tracks and `READ(12)` otherwise, truncating at track end.
- `mmccreate`, `mmcxwrite`, `mmcwrite`, `reserve`, `mmcclose`, and `mmcfixate` manage writable track creation, sector writes, cache sync, track/session close, and TOC refresh.
- `mmcblank`, `format`, `mmcctl`, and `mmcsetspeed` implement control operations.
- Tracks aggregate total written bytes/blocks for diagnostics.

Dependencies:
- Includes Plan 9 SCSI request definitions from `../scuzz/scsireq.h`, plus `dat.h`/`fns.h`.
- Relies on shared `Drive`, `Track`, `Otrack`, `Buf`, and `Scsi` structures.

Research notes:
- The file includes many MMC-6 comments and pragmatic fallbacks for inconsistent drives/media.
- BD detection includes both official structure reads and optional inquiry-string guessing when enabled.
