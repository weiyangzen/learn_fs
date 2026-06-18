<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/filter_seccomp.sh -->
# sources/test-tools/strace/tests/filter_seccomp.sh

## Purpose
Covers the `filter_seccomp.sh` strace test helper script. Source comments describe: # Skip the test if seccomp filter is not available. # Copyright (c) 2018-2019 The strace developers. All rights reserved. # SPDX-License-Identifier: GPL-2.0-or-later Source read: 14 lines, 396 bytes.

## Important APIs, Types, And Functions
includes/imports: none; defines: none.

## Control Flow
Shell control flow runs top to bottom with 0 loop(s) and 0 case block(s), using harness helpers for skip/fail behavior and writing generated or probe output as directed.

## State And Persistence Behavior
Shell state is process-local variables plus intentional output files such as generated scripts, logs, or expected-output artifacts managed by the strace test harness.

## Dependencies And Integration Points
Depends on the built `strace` binary and test harness log/diff helpers. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: seccomp-BPF availability and filter installation can vary by kernel/configuration. Test signals: skip paths report exit 77 rather than failure.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/filter_seccomp.sh -->
