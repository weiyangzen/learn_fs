<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/check-copyright.sh -->
# sources/test-tools/syzkaller/tools/check-copyright.sh

## Purpose

CI lint script enforcing the canonical syzkaller copyright and Apache 2 header on tracked source/config files.

## Important APIs, Types, and Functions

Shell loop over `git ls-files`, regex filters, `tr`, `grep`, generated-file marker checks, and `FILES`/`FAILED` variables.

## Control Flow

Collects eligible tracked files, flattens each file to match the required two-line header, skips known generated files, emits file-position diagnostics for misses, and exits 1 if any file failed.

## State and Persistence Behavior

Reads git index and files only; keeps counters in process memory and writes nothing.

## Dependencies and Integration Points

Requires bash, Git, grep/coreutils, and repo-root execution. Used by presubmit linting.

## Risks and Edge Cases

Command substitution is filename-whitespace fragile; only `//` and `#` headers are accepted; generated marker coverage must stay current.

## Test Signals

Run on compliant, missing-header, generated, vendored, and testdata fixtures.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/check-copyright.sh -->
