# sources/sync-backup/rsync/configure

## Purpose
Bootstrap wrapper for rsync configuration. It ensures generated configure artifacts exist, optionally switches into an auto-prepared build directory, and delegates to `configure.sh` with the correct `--srcdir`.

## Important APIs, Types, and Functions
The script computes `dir` from `$0`, invokes `packaging/prep-auto-dir` when run from the source root, calls `prepare-source build` if `configure.sh` is missing, removes a failed generated `configure.sh`, and finally `exec`s `./configure.sh --srcdir="$dir" "$@"`.

## Control Flow
On startup it normalizes an empty `dirname` result to `.`. If run from `.`, it lets `packaging/prep-auto-dir` decide whether to use `build/`. It then requires `configure.sh`, generating it via `prepare-source build` when absent. Failure emits a clear diagnostic and exits. Success replaces the shell process with the real configure script.

## State and Persistence Behavior
May create or update generated source/configure artifacts through `prepare-source`, may `cd build`, and may delete a failed `configure.sh`. It does not itself produce `config.h` or `Makefile`; that is delegated to `configure.sh`.

## Dependencies and Integration Points
Depends on POSIX shell, `packaging/prep-auto-dir`, `prepare-source`, and generated `configure.sh`. It fronts the Autoconf output described by `configure.ac`.

## Risks and Test Signals
Risks are bootstrap recursion/path mistakes, missing generated files, or stale build-directory selection. Test signals include running `./configure` from a clean checkout without `configure.sh`, from a prepared build dir, and from release tarballs where generated files already exist.
