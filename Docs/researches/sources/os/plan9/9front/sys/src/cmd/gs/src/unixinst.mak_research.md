# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/unixinst.mak

Final Unix makefile fragment containing install targets.

Key points:
- Defines `install` as `install-exec install-scripts install-data`.
- `install-exec` installs the Ghostscript executable into `bindir`.
- `install-scripts` installs command scripts after rewriting `GS_EXECUTABLE=...`.
- Defines library/resource/documentation/example/man source directories relative to `PSLIBDIR`.
- `install-libdata` installs core `.ps`, Fontmap/cidfmap/FAPI files, PPD/RPD/UPP/XBM/XPM files, and generated `gs_*.ps` / `pdf*.ps`.
- `install-resdata` copies all Resource categories except CVS.
- `install-doc` copies selected HTML/text documentation.
- `install-man` installs localized manpages and creates symlinks for related commands.
- `install-examples` installs sample PostScript/PDF/EPS files.

Dependencies and interactions:
- Uses `INSTALL_PROGRAM`, `INSTALL_DATA`, `gsdatadir`, `scriptdir`, `docdir`, `mandir`, and `exdir` from top-level makefiles.
- Included last by Unix makefiles.

Research relevance:
- Defines the runtime filesystem layout of Ghostscript installations produced by this source tree.
