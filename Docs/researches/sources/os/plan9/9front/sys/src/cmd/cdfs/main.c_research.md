# File Research: sources/os/plan9/9front/sys/src/cmd/cdfs/main.c

9P file server presenting CD/DVD/BD drive contents as a filesystem.

Key behavior:
- Exposes root directory, `ctl`, writable audio/data directories `wa`/`wd`, and one file per discovered track.
- `fsattach`, `fsclone`, `fswalk1`, `fsopen`, `fsread`, `fswrite`, `fscreate`, `fsremove`, `fsstat`, and `fsdestroyfid` implement the lib9p server interface.
- `checktoc` refreshes the table of contents and synthesizes track names such as `aNNN`, `dNNN`, `uNNN`, or hidden blank entries.
- `readctl` reports CDDB query data for audio discs, current/max speeds, media type, and next writable sector.
- `writectl` parses speed control commands and passes other control commands to the drive backend.
- Track reads/writes are delegated through `Otrack` and `Buf`.
- `fscreate` creates new writable audio/data tracks under `wa`/`wd`.
- Removing `wa`/`wd` triggers disc fixation.
- `main` opens an SCSI device, probes it through `mmcprobe`, refreshes TOC, and mounts the 9P service.

Dependencies:
- Uses Plan 9 `thread`, `9p`, `disk`, SCSI/MMC backend, and local `dat.h`/`fns.h`.

Research notes:
- This is the user-visible filesystem boundary for optical media.
- Directory qid versions are tied to drive media-change generation.
