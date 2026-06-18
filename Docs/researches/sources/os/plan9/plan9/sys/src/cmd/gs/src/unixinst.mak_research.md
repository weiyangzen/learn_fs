# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/unixinst.mak

Final Unix install-target makefile fragment.

Key points:
- Defines aggregate `install: install-exec install-scripts install-data`.
- `install-exec` installs the Ghostscript executable.
- `install-scripts` installs many helper scripts, rewriting `GS_EXECUTABLE=...` to match `$(GS)`.
- `install-data` delegates to library data, resource data, docs, man pages, and examples.
- `install-libdata` installs Fontmap files, PostScript utility files, `gs_*.ps`, `pdf*.ps`, PPD/RPD/UPP/XBM/XPM files.
- `install-resdata` copies Resource subdirectories except CVS.
- `install-doc` installs a fixed HTML/documentation page list.
- `install-man` installs localized man pages and creates symlinks for related tools.
- `install-examples` installs example PostScript/PDF/EPS files.

Dependencies and interactions:
- Depends on directory variables from the top-level Unix makefiles.
- Uses `instcopy` through `INSTALL_PROGRAM` and `INSTALL_DATA`.

Research relevance:
- Captures Ghostscript’s runtime layout: executable, scripts, lib/resource data, docs, man pages, examples.
