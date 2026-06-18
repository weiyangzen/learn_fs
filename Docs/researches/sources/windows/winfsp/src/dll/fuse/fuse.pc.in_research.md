# File Research: sources/windows/winfsp/src/dll/fuse/fuse.pc.in

Pkg-config template for the WinFsp FUSE-compatible API.

Key contents:
- Sets `prefix` relative to the pc file directory.
- Sets `incdir` to `${prefix}/inc/fuse`.
- Sets `implib` to `${prefix}/bin/winfsp-${arch}.dll`.
- Advertises package name `fuse`, description `WinFsp FUSE compatible API`, version `2.8`, and URL `https://winfsp.dev`.
- Emits `Libs` as the WinFsp DLL path and `Cflags` as the FUSE include directory.

Filesystem relevance:
- Build/distribution metadata that lets FUSE-compatible consumers discover headers and link target for WinFsp.

Notable risks:
- Depends on the packaging environment providing `arch` and placing headers/DLLs at the expected relative locations.
