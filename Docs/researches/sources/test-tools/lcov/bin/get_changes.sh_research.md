# sources/test-tools/lcov/bin/get_changes.sh

## Purpose

`get_changes.sh` prints LCOV change-log information. It prefers live Git history from the LCOV tool directory and falls back to the packaged `../CHANGES` file when Git metadata is unavailable.

## Important APIs, types, and functions

This is a small Bash script with no functions. `TOOLDIR=$(cd $(dirname $0) >/dev/null ; pwd)` resolves the directory containing the script, `cd $TOOLDIR` moves there, and the main command attempts `git --no-pager log --no-merges --decorate=short --color=never`. If that command fails, it runs `cat "$TOOLDIR/../CHANGES" 2>/dev/null`.

## Control flow

The script resolves its directory, changes to it, invokes Git log, and exits with Git's success path if available. On Git failure, the `if ! ...; then` fallback prints the static changes file if present. There is no explicit final status normalization, so the process exit status is the status of the command executed in the selected branch.

## State and persistence behavior

The script writes only to stdout/stderr and does not create files. It changes the process working directory, but that change is confined to the script process.

## Dependencies and integration points

Runtime dependencies are Bash, `dirname`, `cd`, `pwd`, `git`, and `cat`. It integrates with a source checkout containing `.git` history and with release archives containing `sources/test-tools/lcov/CHANGES`.

## Risks and edge cases

- `$0`, `dirname $0`, and `cd $TOOLDIR` are not consistently quoted, so paths containing spaces or glob characters can break.
- If Git exists but the directory is not a repository, the fallback hides Git diagnostics and tries `../CHANGES`.
- If both Git and `../CHANGES` fail, no message is printed and the exit status comes from `cat`.
- The script assumes it should operate from the tool directory rather than the user's current working directory.

## Test signals

Tests should run it in a Git checkout, in a copied tree without `.git` but with `CHANGES`, and in a copied tree without either data source. A path-with-spaces fixture would expose the current quoting weakness.
