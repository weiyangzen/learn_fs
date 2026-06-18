<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/.github/workflows/run.sh -->
# sources/test-tools/syzkaller/.github/workflows/run.sh research

Purpose: wrapper script for GitHub Actions CI commands that sets a stable home/cache directory and converts compiler/test diagnostics into GitHub workflow annotations.

Important APIs, types, and functions: Bash script with `HOME=$PWD`, `.cache` creation, `set -o pipefail`, positional command execution `$1 "${@:2}"`, and a `sed -E` regex that emits `::error file=...,line=...,col=...::...` records.

Control flow: the script runs the requested command, pipes combined stdout through `sed`, and relies on `pipefail` so command failures propagate through the annotation pipeline.

State and persistence: creates `.cache` under the checkout and exports `HOME` for tools that consult user cache/config directories. It does not mutate source files directly.

Dependencies and integration: invoked by `ci.yml` for Makefile presubmit targets. Depends on Bash and GNU/BSD-compatible `sed -E`.

Risks: annotation regex can misclassify arbitrary output that resembles `file:line:` diagnostics. Commands that require stdin interaction are not supported. The script does not quote the command name beyond positional expansion, so callers must pass arguments normally.

Test signals: failing compiler/linter output should appear both as raw log lines and GitHub error annotations; the wrapper should return nonzero when the underlying command fails.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/.github/workflows/run.sh -->
