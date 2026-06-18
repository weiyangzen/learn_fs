<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/configure -->
# sources/storage-engines/sqlite/configure

## Purpose
`configure` is the repository entrypoint for SQLite's autosetup-based configuration system. It is intentionally tiny: it finds the adjacent `autosetup` directory, exports the wrapper path, and replaces the shell process with the Tcl interpreter selected by `autosetup-find-tclsh` running the `autosetup` script.

## Important APIs, Types, And Functions
There are no shell functions or local option parsers in this wrapper. The important variables are `dir`, computed from `dirname "$0"` with `/autosetup` appended, and `WRAPPER`, exported as the original script path. The only command path it owns is the final `exec "\`"$dir/autosetup-find-tclsh"\`" "$dir/autosetup" "$@"`, which preserves all user arguments for autosetup.

The placeholder `#@@INITCHECK@@#` is an autosetup distribution marker rather than executable behavior in this checked-in file.

## Control Flow
Execution is linear. The shell resolves the autosetup directory relative to the invoked script, exports `WRAPPER`, asks `autosetup-find-tclsh` to locate an appropriate Tcl shell, and then `exec`s that Tcl shell with the autosetup program and original arguments. Because `exec` is used, no post-configure shell cleanup path exists in this wrapper.

## State And Persistence Behavior
The wrapper persists no files itself. Its only process-level state mutation is exporting `WRAPPER` for the autosetup Tcl code. All generated build files, cache behavior, compiler probing, and option persistence belong to `autosetup`, not this script.

## Dependencies
It depends on POSIX `/bin/sh`, `dirname`, the sibling `autosetup/autosetup-find-tclsh` helper, and the sibling `autosetup/autosetup` Tcl script. It also assumes the checked-out tree keeps the wrapper and `autosetup` directory in their expected relative layout.

## Integration Points
This is the command users or build automation run as `./configure`. It hands off to SQLite's autosetup infrastructure, which then configures Makefiles and feature options for the rest of the SQLite source tree.

## Risks And Edge Cases
The relative path computation follows the invocation path, so moving the wrapper away from its sibling `autosetup` directory breaks configuration. If `autosetup-find-tclsh` is missing, not executable, or cannot locate Tcl, the shell fails before any autosetup diagnostics can run. The wrapper deliberately does not validate arguments; unknown options are diagnosed by autosetup after handoff.

## Test Signals
Useful checks are execution-oriented: run `./configure --help` from the SQLite source root and from alternate working directories, verify it finds Tcl through `autosetup-find-tclsh`, and verify all arguments arrive unchanged at autosetup. There is no local unit-test seam in this four-line script.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/configure -->
