# File Research: sources/os/plan9/9front/sys/src/cmd/dossrv/xfile.c

## Purpose
Manages `Xfs` filesystem attachments and `Xfile` fid records for `dossrv`.

## Key Behavior
- `getxfs()` opens the requested device/file, optionally parses a `name:offset` suffix for embedded FAT filesystems, falls back to read-only open when write open fails, and reuses an existing live `Xfs` by qid/name/offset.
- Maintains reference counts for attached filesystems and frees device name, `Dosbpb`, cached buffers, and fd when the last reference drops.
- `xfile()` manages fid lookup, allocation, cleaning, and clunking through a 127-bucket hash table plus freelist.
- `clean()` releases any held `Dosptr` and decrements the referenced `Xfs`.
- `dosptrreloc()` updates other fids pointing at a DOS directory entry when a rename/move changes its sector/offset, preserving qid consistency.

## Interfaces And Dependencies
- Uses `deffile`, `readonly`, `errno`, and `chat()` globals.
- Works with `Dosptr`, `Xfs`, and `Xfile` from `dat.h`, and cache cleanup from `iotrack.c`.

## Notes
The `name:offset` handling mutates the input name string at the colon and assumes 512-byte units for the offset suffix.
