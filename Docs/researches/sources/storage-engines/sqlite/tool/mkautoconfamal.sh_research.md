# sources/storage-engines/sqlite/tool/mkautoconfamal.sh

## Purpose
`mkautoconfamal.sh` builds SQLite's amalgamation autoconf distribution tarball from already-generated amalgamation inputs and the full SQLite source tree. It stages files into a temporary package directory, adds Tcl extension glue, cleans build/editor remnants, runs configure/dist, renames the produced package to the autoconf artifact name, and places the final `.tar.gz` in the caller's working directory.

## Important APIs, Types, and Functions
- Shell variables: `TMPSPACE=./mkpkg_tmp_dir`, `VERSION`, `HASH`, `DATETIME`, and `TARBALLNAME`.
- Inputs from current directory: `sqlite3.c`, `sqlite3.h`, `sqlite3ext.h`, `sqlite3rc.h`, and `shell.c`.
- Inputs from `$TOP`: `VERSION`, `manifest.uuid`, `manifest`, `autoconf`, `autosetup`, `configure`, `sqlite3.1`, `sqlite3.pc.in`, `src/sqlite3.rc`, `tool/Replace.cs`, `main.mk`, `make.bat`, and `src/tclsqlite.c`.
- Generated file: `tea/generic/tclsqlite3.c`, beginning with a `USE_SYSTEM_SQLITE` conditional and then appending SQLite's Tcl binding source.

## Control Flow
1. The script enables `set -e` and `set -u`.
2. It reads version and manifest metadata from `$TOP`.
3. It chooses `TARBALLNAME`: for normal release-style invocation, it converts `3.x.y[.z]` into `sqlite-autoconf-3xxyyzz`; for `--snapshot` or no matching non-snapshot branch, it uses `sqlite-snapshot-$DATETIME`.
4. It removes and recreates the staging area by copying autoconf infrastructure and amalgamation/source files into `./mkpkg_tmp_dir`.
5. It prints the staging tree, changes into the staging directory, creates Tcl wrapper source, deletes editor/build artifacts, runs `./configure && ${MAKE-make} dist`, unpacks the produced `sqlite-$VERSION.tar.gz`, renames it to `$TARBALLNAME`, repacks it, moves the final tarball to the parent directory, and lists it.

## State and Persistence Behavior
- Destructively removes `./mkpkg_tmp_dir` on every run.
- Produces `$TARBALLNAME.tar.gz` one directory above the staging directory, normally the original current working directory.
- Reads source-tree metadata but does not modify `$TOP`.
- Uses `${MAKE-make}` so the environment can select a make implementation.

## Dependencies and Integration Points
- Requires a POSIX-ish `/bin/sh`, `cat`, `cut`, `grep`, `tr`, `sed`, `printf`, `rm`, `cp`, `tree`, `mkdir`, `find`, `configure`, `make`, `tar`, and `ls`.
- Integrates with SQLite release/build artifacts; it assumes the amalgamation files already exist in the current directory and `$TOP` points to the source root.
- The generated autoconf tarball is a release/distribution artifact rather than a normal build output.

## Risks and Edge Cases
- `rm -rf $TMPSPACE` is intentionally destructive; running from the wrong directory can delete a local directory with the same name.
- Variables are unquoted in many commands, so spaces or shell metacharacters in `$TOP`, `$VERSION`, or paths can break the script.
- The argument condition appears inverted relative to the comment: the normal autoconf naming branch is taken when at least one argument exists and `$1` is not `--snapshot`; otherwise snapshot naming is used.
- The script assumes `tree` is installed, which may not hold on minimal builders.
- `HASH` is computed but unused.
- Build output depends on the host toolchain and configure behavior.

## Test Signals
- Run from a clean amalgamation directory with valid `$TOP` and verify the tarball name, contents, and included Tcl wrapper.
- Test `--snapshot` and release-version naming explicitly.
- Run with missing required files to confirm `set -e` stops early.
- Inspect the tarball for absence of `*~`, `#*#`, `*.o`, and `*.so` remnants.
