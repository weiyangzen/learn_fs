# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/unix-dll.mak

Unix shared object build fragment.

Key points:
- Defines `so`, `sodebug`, `install-so`, `soinstall`, `SODIRS`, and `soclean` targets.
- Builds shared library names `lib$(GS).so`, major symlink, and major/minor versioned library.
- Builds small loader executables: console `$(GS)c` and Gtk/display-capable `$(GS)x`.
- Uses recursive make with `SODEFS` to redirect object/bin dirs to `../soobj` and `../sobin`, enable `-shared`, set soname, and force `STDIO_IMPLEMENTATION=c`.
- Installs shared library and loader symlinks under `$(libdir)` and `$(bindir)`.

Dependencies and interactions:
- Included by `unix-gcc.mak`.
- Relies on `GS_VERSION_MAJOR` and `GS_VERSION_MINOR` from `version.mak`.

Research relevance:
- Documents Ghostscript’s legacy Unix shared-library packaging and loader architecture.
