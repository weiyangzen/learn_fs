# sources/test-tools/lcov/bin/fix.pl

Purpose: Perl release/install fixup utility that rewrites version strings, release numbers, dates, interpreter paths, library paths, binary paths, script paths, RPM spec metadata, and optional version files across lcov artifacts.

Important APIs/types/functions: `Getopt::Long`; environment variables `V`, `SOURCE_DATE_EPOCH`, `LCOV_PERL_PATH`, and `LCOV_PYTHON_PATH`; functions `get_file_info`, `update_man_page`, `update_perl`, `update_python`, `update_txt_file`, `update_spec_file`, `write_version_file`, `guess_filetype`, `usage`, and `main`.

Control flow: options select file type explicitly or allow `guess_filetype` from shebang, extension, man macros, spec markers, or text heading patterns. `main` optionally writes a version file, then for each file reads the full source, computes date/mode info, applies requested transforms for matching type, writes changed content through `filename.new`, preserves mode, renames atomically enough for local filesystems, and restores mtime using the selected epoch. Manpages get `LCOV <version>`, escaped dates, and `.ds scriptdir`. Perl tools get `$VERSION`, optional shebang replacement, and `FindBin` path rewrites. Python gets optional shebang replacement. Text files get `Last changes:` dates. Spec files get `Version:` and `Release:`.

State/persistence behavior: mutates input files in place when content changes, writes optional `--verfile`, preserves permissions, and sets atime/mtime to the chosen timestamp. It may remove `use FindBin;` lines when path rewrites are requested.

Dependencies/integration: heavily used by the Makefile during install, dist, RPM, and release flows. It encodes install-time paths such as libdir/bindir/scriptdir and release metadata into scripts, libraries, docs, README, and RPM spec files.

Risks/test signals: regex rewrites assume stable formatting and may miss changed declarations or replace unintended matching lines. `update_perl` skips shebang replacement for exactly `/usr/bin/env perl`, which may be intentional but surprising with `--fixinterp`. `SOURCE_DATE_EPOCH` is capped by file mtime, so future or externally supplied epochs newer than the file are not used. Signals include diffing rewritten artifacts, preserving executable modes, correct `.version` contents, and staged install scripts resolving installed paths instead of source-tree `FindBin` paths.
