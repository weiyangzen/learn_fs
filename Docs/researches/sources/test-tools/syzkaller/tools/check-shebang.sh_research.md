<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/check-shebang.sh -->
# sources/test-tools/syzkaller/tools/check-shebang.sh

## Purpose

Executable shebang portability lint.

## Important APIs, Types, and Functions

Uses `git ls-files -s` mode `100755`, `head`, and `grep -E` to inspect executable tracked files.

## Control Flow

Checks executable non-generated files, allows `/bin/sh` and `/usr/bin/env ...`, reports other shebang interpreters, and fails if any are found.

## State and Persistence Behavior

Reads Git modes and first lines only; no writes.

## Dependencies and Integration Points

Depends on Git, bash, head/grep, and executable bit correctness in the index.

## Risks and Edge Cases

Filename splitting is whitespace-fragile; policy deliberately rejects otherwise common `/bin/bash` shebangs.

## Test Signals

Fixtures with `/bin/sh`, `/usr/bin/env bash`, `/bin/bash`, no shebang, generated executable.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/check-shebang.sh -->
