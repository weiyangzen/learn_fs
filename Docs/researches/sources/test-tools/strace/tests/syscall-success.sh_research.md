<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/syscall-success.sh -->
# sources/test-tools/strace/tests/syscall-success.sh

## Purpose
Covers the `syscall-success.sh` shell harness test. Source comments/macros state: # Check decoding of a syscall using syscall injection. # Accepts a list of retvals to inject as the first INJECT_RETVALS= argument Accepts a syscall to inject retvals to as the first INJECT_SYSCALL= argument # Copyright (c) 2018-2026 The strace developers. All rights reserved. # SPDX-License-Identifier: GPL-2.0-or-later We avoid messing with arguments by accepting arguments we understand only at the beginning of. Source read: 46 lines, 1126 bytes.

## Important APIs, Types, And Functions
includes/imports: none; defines/undefs: none; harness commands: check_prog sed, run_strace -e "inject=${INJECT_SYSCALL}:retval=${i}" "$@" \, match_diff "$LOG.$i" "$EXP.$i".

## Control Flow
Shell flow runs top to bottom through harness initialization, feature checks, strace invocation, and result matching. The script contains 2 loop(s), 2 case block(s), and exits through harness skip/fail helpers when prerequisites are absent.

## State And Persistence Behavior
Shell state is process-local variables, temporary files, generated expected-output logs, and harness-controlled exit status.

## Dependencies And Integration Points
Depends on built `strace` binary and shell harness. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: unsupported environments skip rather than fail; harness performs exact diff comparison.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/syscall-success.sh -->
