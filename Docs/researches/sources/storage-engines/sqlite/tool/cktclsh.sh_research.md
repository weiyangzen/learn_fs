# sources/storage-engines/sqlite/tool/cktclsh.sh

## Purpose
`cktclsh.sh` checks that a given Tcl shell executable is at least a requested Tcl version. It is used by make targets that require a minimum Tcl version.

## Important APIs, Types, and Functions
The script writes a temporary Tcl file named `cktclsh$1.tcl` containing a version comparison against `$tcl_version`, runs it with the Tcl shell in `$2`, and removes the temp file. Its interface is positional: `$1` is minimum version and `$2` is the Tcl shell command.

## Control Flow
It creates the Tcl script, executes it, and if the interpreter exits unsuccessfully, prints an error, removes the temp script, and exits 1. On success it removes the temp file and exits with the shell's default success.

## State and Persistence
The only file-system state is the temporary script in the current directory. It is normally removed, but interruption could leave it behind.

## Dependencies and Integration Points
Dependencies are Bourne shell and a Tcl interpreter. It integrates with SQLite makefiles and build checks.

## Risks
The temp filename is predictable and based only on the version string, so concurrent runs in the same directory can race. There is no argument validation or shell quoting around `$2`, so callers must pass a safe command path. Version comparison uses Tcl string/numeric semantics through `$tcl_version<$vers`.

## Test Signals
Run with Tcl versions below and above the threshold, missing Tcl executable, malformed version strings, and concurrent invocations in the same directory.
