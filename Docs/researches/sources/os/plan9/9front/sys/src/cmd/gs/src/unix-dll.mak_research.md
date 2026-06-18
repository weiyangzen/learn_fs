# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/unix-dll.mak

Unix shared-object build fragment for Ghostscript.

Key points:
- Defines shared-object build directories `../soobj` and `../sobin`.
- Defines small loader executables `gsc` and `gsx`; `gsx` links GTK display support via `gtk-config`.
- Defines shared library names and symlink chain: `lib$(GS).so`, `.major`, and `.major.minor`.
- Uses recursive make with `SODEFS` to build the shared library with `-shared`, `-soname`, PIC flags, alternate object directories, `STDIO_IMPLEMENTATION=c`, and display device override.
- Provides targets `so`, `sodebug`, `install-so`, `soinstall`, `SODIRS`, and `soclean`.
- Installs loaders and the shared library into `bindir` / `libdir`.

Dependencies and interactions:
- Included by `unix-gcc.mak`.
- Uses `GS_VERSION_MAJOR`, `GS_VERSION_MINOR`, and `GS_SONAME*` values from `version.mak` and local variables.
- Relies on normal Unix build targets via recursive make.

Research relevance:
- Documents how this Ghostscript snapshot could build a Unix shared library plus small loader binaries before the newer configure-based build style.
