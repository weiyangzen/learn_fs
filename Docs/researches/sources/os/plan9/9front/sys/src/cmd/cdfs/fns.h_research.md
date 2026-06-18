# File Research: sources/os/plan9/9front/sys/src/cmd/cdfs/fns.h

Shared function declarations for `cdfs`.

Key declarations:
- Buffer API: `bopen`, `bread`, `bwrite`, `bterm`, `bufread`, `bufwrite`.
- Utility/API declarations: `disctype`, `emalloc`, `geterrstr`, and `mmcprobe`.

Dependencies:
- Uses `Buf`, `Otrack`, `Drive`, and `Scsi` types from `dat.h` and included system headers.

Research notes:
- This header is intentionally small and only exposes cross-module entry points.
