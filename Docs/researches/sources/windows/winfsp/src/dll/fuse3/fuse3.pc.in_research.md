# File Research: sources/windows/winfsp/src/dll/fuse3/fuse3.pc.in

This is the pkg-config template for the WinFsp FUSE3-compatible API.

Key fields:
- `prefix=${pcfiledir}/..`
- headers under `inc/fuse3`
- import library path pointing at `bin/winfsp-${arch}.dll`
- package name `fuse3`
- description `WinFsp FUSE3 compatible API`
- version `3.2`
- URL `https://winfsp.dev`
- emits `Libs` and `Cflags` for consumers.

Filesystem relevance:
- Build/distribution metadata only; no runtime filesystem logic.
