<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/init-once.sh -->
# sources/test-tools/strace/tests/init-once.sh

## Purpose
Covers the shared strace test-shell framework loaded once by generated and handwritten tests. Source comments describe: # Copyright (c) 2011-2016 Dmitry V. Levin <ldv@strace.io> Copyright (c) 2011-2026 The strace developers. All rights reserved. # SPDX-License-Identifier: GPL-2.0-or-later Starting with glibc 2.43, support for 2MB transparent huge pages has been enabled by default in malloc on AArch64. Disable it to avoid unexpected madvise() and close() invocations that. Source read: 1045 lines, 25142 bytes.

## Important APIs, Types, And Functions
includes/imports: none; defines: none; shell functions: warn_, fail_, skip_, framework_failure_, framework_skip_, sed_re_escape, sed_slash_escape, get_prefix_value, sq_root, get_config_str, get_config_option, print_current_personality_designator, check_prog, dump_log_and_fail_with, run_prog, run_prog_skip_if_failed, try_run_prog, run_strace, run_strace_merge, check_gawk, match_awk, match_diff, match_grep, timing_quant_slack.

## Control Flow
Initializes common environment variables, defines skip/fail helpers, program checks, strace execution wrappers, diff/grep/AWK matchers, timing comparators, seccomp/kernel feature probes, and final per-test setup. It is meant to be sourced, not executed as an isolated test body.

## State And Persistence Behavior
Shell state is process-local variables plus intentional output files such as generated scripts, logs, or expected-output artifacts managed by the strace test harness.

## Dependencies And Integration Points
Depends on `init.sh`, the built `strace` binary and test harness log/diff helpers. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: pid namespace translation is sensitive to namespace support and parent/child synchronization; timing/performance checks need tolerance for scheduler noise. Test signals: harness uses exact diff matching; harness uses regex/grep matching; skip paths report exit 77 rather than failure.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/init-once.sh -->
