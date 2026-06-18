<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/autoconf/tea/configure -->
# sources/storage-engines/sqlite/autoconf/tea/configure

## Purpose
This shell wrapper locates the appropriate autosetup directory for a teaish extension and execs autosetup through a discovered Tcl/Jim interpreter. It lets extension-local `configure` work whether teaish is in a local copy, SQLite autoconf bundle, or canonical SQLite source tree.

## Important APIs, Types, And Functions
The script is pure POSIX shell. It uses `dirname "$0"` to derive `dir0`, probes `$dirA/autosetup`, `$dirA/../autosetup`, and `$dirA/../../autosetup`, exports `WRAPPER="$0"`, invokes `"$dirA/autosetup-find-tclsh"` in command substitution, and execs `"$dirA/autosetup"` with `--teaish-extension-dir="$dir0"` plus all user arguments.

## Control Flow
The wrapper starts with the extension directory, checks the three supported autosetup locations in order, and exits with an error if none exists. On success it transfers control with `exec` to the interpreter returned by `autosetup-find-tclsh`, passing autosetup itself and extension-dir metadata.

## State And Persistence Behavior
The only state is environment variable `WRAPPER`, which autosetup uses to identify invocation through a configure wrapper and locate `auto.def`. No files are created by this wrapper directly.

## Dependencies And Integration Points
It depends on the autosetup launcher, `autosetup-find-tclsh`, a usable `tclsh`/`jimsh` or bootstrap path, and the teaish autosetup modules. It integrates extension configuration with SQLite's bundled autosetup layouts.

## Risks
The directory tests are unquoted (`[ -d $dirA/... ]`), so paths with spaces can break. Failure to find autosetup yields an immediate error. Because it uses `exec`, any interpreter lookup failure or autosetup error becomes the configure result.

## Test Signals
Useful checks are running this `configure` from each supported tree layout, verifying that `WRAPPER`-based source directory detection works, and confirming `--teaish-extension-dir` reaches autosetup-generated teaish configuration.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/autoconf/tea/configure -->
