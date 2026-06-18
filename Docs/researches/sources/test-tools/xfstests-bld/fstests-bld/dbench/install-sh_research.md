<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/dbench/install-sh -->
# sources/test-tools/xfstests-bld/fstests-bld/dbench/install-sh

Source read: complete file, 238 lines, 4773 bytes, sha256 `593667e06b70dbc89d41a88c790691ff09349a4427557730fd81ea2accac6ad6`. Final split target: `Docs/researches/sources/test-tools/xfstests-bld/fstests-bld/dbench/install-sh_research.md`.

Purpose: portable X11R5-style install helper used by generated makefiles when a platform lacks a suitable BSD-compatible `install` command. It installs files or creates directories while applying mode, owner, group, strip, and optional filename transformations.

Important APIs/types/functions: command-line options include `-c` for copy instead of move, `-d` for directory creation, `-m MODE`, `-o OWNER`, `-g GROUP`, `-s` for strip, `-t=SED_EXPR`, and `-b=SUFFIX`. Environment overrides such as `MVPROG`, `CPPROG`, `CHMODPROG`, `DOITPROG`, and related variables let makefiles substitute tool paths or dry-run behavior.

Control flow: parses options into shell command variables; validates source/destination unless in directory mode; treats directory destinations by appending the source basename; computes `dstdir`; creates missing parent directories component by component; for directory mode creates/chowns/chgrps/strips/chmods the directory; for file mode installs into a temporary `#inst.$$#`, applies attributes, removes the final destination, and renames the temp file atomically into place.

State and persistence behavior: creates directories, copies or moves files, may remove an existing destination, may strip binaries, and applies ownership/mode changes. It installs via a temp file in the destination directory and cleans it through a shell trap.

Dependencies and integration: used by autoconf/automake-like build rules through `INSTALL`, `INSTALL_PROGRAM`, `INSTALL_DATA`, or `INSTALL_SCRIPT`. Depends on POSIX shell plus `mv`, `cp`, `chmod`, `chown`, `chgrp`, `strip`, `rm`, `mkdir`, `basename`, and `sed`.

Risks: many variable expansions are unquoted, so paths with spaces, shell metacharacters, or leading dashes can misbehave. Temporary filename `#inst.$$#` can collide in unusual concurrent scenarios. Ownership changes require privileges and can fail late after the temp file is created.

Test signals: `make install DESTDIR=...` or direct dry-run with `DOITPROG=echo` should show the intended parent directory creation, temp install, chmod, and final rename. Smoke tests should include file install to an existing directory and `-d` hierarchy creation.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/dbench/install-sh -->
