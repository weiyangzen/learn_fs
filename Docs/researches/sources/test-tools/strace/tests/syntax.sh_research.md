<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/syntax.sh -->
# sources/test-tools/strace/tests/syntax.sh

## Purpose
Covers the `syntax.sh` shell harness test. Source comments/macros state: # Define syntax testing primitives. # Copyright (c) 2016 Dmitry V. Levin <ldv@strace.io> Copyright (c) 2016-2024 The strace developers. All rights reserved. # SPDX-License-Identifier: GPL-2.0-or-later Source read: 89 lines, 1753 bytes.

## Important APIs, Types, And Functions
includes/imports: none; defines/undefs: none; shell functions: log_sfx, check_zero, check_exit_status_and_stderr, check_exit_status_and_stderr_using_grep, check_e, check_e_using_grep, check_h; harness commands: check_zero(), $STRACE "$@" 2> "$LOG.$sfx" > /dev/null || {, check_exit_status_and_stderr(), $STRACE "$@" 2> "$LOG.$sfx" && {, match_diff "$LOG.$sfx" "$EXP.$sfx" \, check_exit_status_and_stderr_using_grep(), match_grep "$LOG.$sfx" "$EXP.$sfx" \, check_e(), $STRACE_EXE: $pattern, check_exit_status_and_stderr "$sfx" "$@".

## Control Flow
Shell flow runs top to bottom through harness initialization, feature checks, strace invocation, and result matching. The script contains 2 loop(s), 0 case block(s), and exits through harness skip/fail helpers when prerequisites are absent.

## State And Persistence Behavior
Shell state is process-local variables, temporary files, generated expected-output logs, and harness-controlled exit status.

## Dependencies And Integration Points
Depends on `init.sh`, built `strace` binary and shell harness. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: harness performs exact diff comparison; harness performs regex/grep matching.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/syntax.sh -->
