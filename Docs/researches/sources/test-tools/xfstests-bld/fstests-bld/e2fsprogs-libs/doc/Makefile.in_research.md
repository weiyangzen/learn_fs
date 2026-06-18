<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/doc/Makefile.in -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/doc/Makefile.in

## Purpose
This make template builds and installs libext2fs documentation from Texinfo sources. It produces Info and DVI outputs by default, can generate split HTML, installs compressed Info files, and defines cleanup targets for generated documentation artifacts.

## Important APIs, Types, and Functions
Important make targets are `all`, `install-doc-libs`, `uninstall-doc-libs`, `libext2fs.info`, `libext2fs.dvi`, `libext2fs_abt.html`, `distclean`, `clean`, `clean-all`, `clean-final`, `clean-tex`, `clean-backup`, `clean-tarfiles`, and `clean-html`. It consumes `@MCONFIG@` for common install variables and `@MAKEINFO@` from configure.

## Control Flow
`all` depends on Info and DVI generation. Install removes old `libext2fs.info*`, creates `$(infodir)`, copies matching Info files, and gzips them. Individual document targets invoke `makeinfo`, `texi2dvi`, or `texi2html`; failures are prefixed with `-`, making documentation generation non-fatal in many paths.

## State and Persistence
Generated files persist in the doc build directory: `.info`, `.dvi`, `.html`, Texinfo auxiliary files, archives, and backups. Install persists compressed Info files under `$(DESTDIR)$(infodir)`.

## Dependencies and Integration Points
The template depends on `libext2fs.texinfo`, configured install tools from `MCONFIG`, `makeinfo`, `texi2dvi`, `texi2html`, `gzip`, and directory creation via `MKINSTALLDIRS`. It is emitted by `configure.in` as `doc/Makefile` when the source doc directory exists.

## Risks
Documentation generation is often non-fatal, so missing or broken tools may produce a successful build without docs. The HTML target assumes `texi2html -split_chapter` creates a `libext2fs` subdirectory. Cleanup rules are broad within the doc directory and remove generated artifacts by extension.

## Test Signals
Signals include `make -C doc all` producing Info/DVI when tools exist, `make install-doc-libs DESTDIR=...` creating gzipped Info files, and cleanup targets removing only expected generated documentation files.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/doc/Makefile.in -->
