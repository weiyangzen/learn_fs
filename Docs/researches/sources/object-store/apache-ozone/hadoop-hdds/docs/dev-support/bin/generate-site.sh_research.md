# sources/object-store/apache-ozone/hadoop-hdds/docs/dev-support/bin/generate-site.sh

## Purpose
This Bash script builds the HDDS documentation site with Hugo into the Maven output directory. It is designed to be invoked from the docs build/check flow and to skip cleanly when Hugo is unavailable.

## Important variables and commands
- `set -eu` exits on unset variables and failed commands.
- `DIR` resolves the script directory via `${BASH_SOURCE[0]}`.
- `DOCDIR="$DIR/../.."` points to the docs module root.
- `which hugo` gates execution; if Hugo is missing, it prints a skip message and exits `0`.
- `OZONE_VERSION` is exported from `mvn help:evaluate -Dexpression=ozone.version -q -DforceStdout -Dscan=false`.
- `ENABLE_GIT_INFO` becomes `--enableGitInfo` if `git -C $(pwd) status` succeeds.
- Output directory is `$DOCDIR/target/classes/docs`.
- Main build command is `hugo "${ENABLE_GIT_INFO}" -d "$DESTDIR" "$@"`.

## Control flow
The script resolves paths, checks for Hugo, computes the Ozone version from Maven, conditionally enables Hugo Git metadata, creates the destination directory, changes into the docs directory, invokes Hugo with any caller-provided arguments, and returns to the previous directory with `cd -`.

## State and persistence
The script writes generated static docs into `hadoop-hdds/docs/target/classes/docs`. It also exports `OZONE_VERSION` for the Hugo process. It does not persist any state outside generated output.

## Dependencies and integration points
Dependencies are Bash, `hugo`, `mvn`, `git`, the docs `config.yaml`, and the `ozonedoc` Hugo theme. The Maven docs module and `hadoop-ozone/dev-support/checks/docs.sh` are likely callers through the docs `pom.xml`.

## Risks and edge cases
- Missing Hugo is treated as a successful skip, so CI must separately decide whether skipped docs are acceptable.
- `git -C $(pwd)` leaves `$(pwd)` unquoted; unusual working directories with whitespace would break this check.
- Passing an empty `ENABLE_GIT_INFO` as a quoted argument may produce an empty Hugo argument; most shells pass it as `""`, which Hugo generally tolerates but is less clean than an array.
- Maven version evaluation failure aborts the script because of `set -e`.
- `cd -` prints the previous directory, which can add noise to build logs.

## Test signals
Run with Hugo absent to confirm exit `0` and skip message. Run with Hugo present to confirm `target/classes/docs` is populated, the generated site sees `OZONE_VERSION`, user-provided Hugo args are passed through, and Git info is enabled only inside a Git worktree. Shellcheck would flag the unquoted `$(pwd)` and empty-argument pattern.
