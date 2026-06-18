<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/config/install-sh -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/config/install-sh

Source read: complete file, 238 lines, 4772 bytes, sha256 `8c0dd928b0220f15e6690ef2ca9763a16d08711ac8707421ba74dee5092084cc`. Final split target: `Docs/researches/sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/config/install-sh_research.md`.

Purpose: portable BSD-compatible install helper for e2fsprogs-libs configure/make installations. It mirrors the dbench `install-sh` behavior for file installs and directory creation.

Important APIs/types/functions: supports `-c`, `-d`, `-m`, `-o`, `-g`, `-s`, `-t=`, and `-b=`; uses environment-overridable tools `MVPROG`, `CPPROG`, `CHMODPROG`, `CHOWNPROG`, `CHGRPPROG`, `STRIPPROG`, `RMPROG`, `MKDIRPROG`, and `DOITPROG`.

Control flow: parses options, validates inputs, detects directory mode, appends source basename for directory destinations, computes and creates parent directory hierarchy, then either creates the target directory with requested attributes or installs a file via destination-local temp file, attribute changes, removal of old target, and rename.

State and persistence behavior: creates or updates installed files/directories, removes overwritten destination files, applies permissions/ownership/group, and may strip binaries. Temporary install files are cleaned on exit.

Dependencies and integration: used by autoconf-generated install variables in `MCONFIG.in` and subdirectory makefiles. Depends on POSIX shell and standard file utilities.

Risks: unquoted shell variables make whitespace/metacharacter paths unsafe. The file initializes `tranformbasename` with a typo while later using `transformbasename`; because both default empty and option parsing assigns the correct variable, behavior is effectively unaffected. Temp filename and non-atomic parent directory creation are old-script limitations.

Test signals: run `make install DESTDIR=...` and direct `config/install-sh -d` / file install smoke tests, optionally with `DOITPROG=echo` to inspect commands. Compare behavior with the dbench copy if consolidating scripts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/config/install-sh -->
