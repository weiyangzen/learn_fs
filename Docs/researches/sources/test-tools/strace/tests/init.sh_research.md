<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/init.sh -->
# sources/test-tools/strace/tests/init.sh

## Purpose
Covers the lightweight loader that sources the shared strace test framework once. Source comments describe: # Copyright (c) 2025 Dmitry V. Levin <ldv@strace.io> All rights reserved. # SPDX-License-Identifier: GPL-2.0-or-later Source read: 11 lines, 229 bytes.

## Important APIs, Types, And Functions
includes/imports: none; defines: none.

## Control Flow
Guards on `TESTS_INIT_LOADED`; when not set, computes `srcdir`, sources `init-once.sh`, and prevents duplicate helper definition on later sourcing.

## State And Persistence Behavior
Shell state is process-local variables plus intentional output files such as generated scripts, logs, or expected-output artifacts managed by the strace test harness.

## Dependencies And Integration Points
Depends on `init-once.sh`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: successful compilation and harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/init.sh -->
