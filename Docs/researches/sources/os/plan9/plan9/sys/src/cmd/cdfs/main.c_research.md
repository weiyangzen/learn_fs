# File Research: sources/os/plan9/plan9/sys/src/cmd/cdfs/main.c

This file is the `cdfs` 9P filesystem server entry point and request handler.

Key behavior:
- Exposes a mounted namespace with root, `ctl`, optional audio-write `wa`, optional data-write `wd`, and one file per discovered track.
- `fsattach()`, `fsclone()`, and `fswalk1()` manage lib9p fid state and namespace traversal.
- `fscreate()` creates a writable audio/data track through the drive method table.
- `fsremove()` on `wa`/`wd` finalizes/fixates media.
- `fillstat()` synthesizes directory entries and track file metadata.
- `readctl()` reports CDDB query data for audio discs, speed info, media type, and next writable sector.
- `fsread()` serves directories, `ctl`, and track data; track reads go through the current `Otrack`.
- `writectl()` parses control commands such as `speed`, forwarding other commands to the drive.
- `fswrite()` writes to an open writable track.
- `fsopen()` validates modes and opens track readers.
- `fsdestroyfid()` closes referenced open tracks and refreshes the TOC.
- `checktoc()` refreshes media state and assigns names like `d000`, `a001`, or blank-suppressed entries.
- `main()` opens the SCSI device, probes MMC, initializes the TOC, and mounts the service.

Important details:
- Default device is `/dev/sdD0`; default mount point is `/mnt/cd`.
- Verbose mode redirects stdout/stderr to `/tmp/cdfs.log`.
- Qid versions use drive media change counters to invalidate stale directory state.
- Track file sizes are bytes, while lower-level MMC I/O works in media blocks.

Filesystem relevance:
- Direct. This is the user-facing CD/DVD/BD filesystem server.
