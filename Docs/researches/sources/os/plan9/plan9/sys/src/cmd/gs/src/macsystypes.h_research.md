# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/macsystypes.h

`macsystypes.h` is a substitute `sys/types.h` for the classic Mac CodeWarrior project path. `macos-mcp.mak` copies it to `obj/sys/types.h`.

It includes `<MacTypes.h>` and `<unix.h>`, defines `CHECK_INTERRUPTS`, sets `GX_COLOR_INDEX_TYPE` to `UInt64`, remaps `main` to `gs_main`, and ensures `__MACOS__` is defined.

There is disabled experimental wrapping for `fprintf`, `fputs`, and `getenv`. The header exists to let Ghostscript’s Unix-flavored includes compile under the old Mac toolchain.
