# sources/sync-backup/rsync/install-sh

## Purpose

`install-sh` is a portable shell implementation of the classic BSD/X11 install command. It installs files or creates directories during the build, with options for copy mode, permissions, owner/group changes, stripping, and filename transformation.

## Important APIs, Types, And Functions

The script is pure POSIX-style shell. It honors environment overrides `DOITPROG`, `MVPROG`, `CPPROG`, `CHMODPROG`, `CHOWNPROG`, `CHGRPPROG`, `STRIPPROG`, `RMPROG`, and `MKDIRPROG`. Supported options are `-c` to copy instead of move, `-d` to create a directory, `-m MODE`, `-o OWNER`, `-g GROUP`, `-s` to strip, `-t=SED_EXPR` to transform the basename, and `-b=SUFFIX` for transform basename handling.

## Control Flow

The argument parser records one source and one destination unless `-d` is used, in which case the source becomes the directory destination. It validates required operands and source existence, appends the source basename when destination is an existing directory, computes `dstdir` through sed, creates missing parent directories component by component, then either creates/configures the target directory or installs a file.

For file installation, it computes the final destination filename, applies optional basename transformation, creates a temporary file named `_inst.$$_` in the destination directory, moves or copies the source to the temp file, installs a trap to remove the temp file on exit, applies owner, group, strip, and mode commands, removes any old destination, and renames the temp file into place.

## State And Persistence

Persistent effects are filesystem changes only: parent directory creation, final file/directory creation, ownership/group/mode changes, optional stripping, and temporary file cleanup. `DOITPROG=echo` can turn actions into dry-run command printing.

## Dependencies And Integration Points

The script is used by make/install workflows and avoids relying on a platform `install` binary. It depends on shell, `sed`, `basename`, and the configured file utilities. The name `install-sh` avoids make implicit-rule conflicts with a target named `install`.

## Risks

The script is old and only lightly quoted. Paths with spaces, glob characters, leading dashes, or unusual IFS characters are risky in several tests and command invocations. Parent directory creation uses sed and `set -` path splitting rather than `mkdir -p`. Temporary file names use `$$`, which can collide in hostile/shared directories. Removing the old destination before the final move means a failure during `mv` can leave no installed file.

## Test Signals

Test regular file install, directory creation, install into existing directory, mode/owner/group/strip options, transform options, `DOITPROG=echo`, missing source/destination errors, nested parent creation, and paths containing spaces or shell metacharacters to document current portability limits.
