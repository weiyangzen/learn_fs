<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/gen_tests.in -->
# sources/test-tools/strace/tests/gen_tests.in

## Purpose
Covers the generated strace test manifest with 1324 active test rows. Source comments describe: RLIMIT_??? PR_??? PR_??? PR_??? PR_??? PR_??? PR_??? PR_??? PR_??? PR_??? RLIMIT_??? RLIMIT_??? RLIMIT_??? RLIMIT_??? RLIMIT_??? Input for gen_tests.sh # Copyright (c) 2017-2026 The strace developers. All rights reserved. # SPDX-License-Identifier: GPL-2.0-or-later Source read: 1331 lines, 70936 bytes.

## Important APIs, Types, And Functions
includes/imports: none; defines: none.

## Control Flow
Declarative table consumed sequentially by `gen_tests.sh`; each row maps a test name to optional argv0/script selector and strace arguments. First active rows include _newselect, _newselect-P, accept, accept4, access, access--secontext, access--secontext_full, access--secontext_full_mismatch, access--secontext_mismatch, acct.

## State And Persistence Behavior
The file is declarative manifest state. It does not execute by itself; persistence is the checked-in table content consumed by `gen_tests.sh` to regenerate test scripts.

## Dependencies And Integration Points
Depends on the built `strace` binary and test harness log/diff helpers. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: pid namespace translation is sensitive to namespace support and parent/child synchronization; seccomp-BPF availability and filter installation can vary by kernel/configuration; module syscalls may be blocked by privileges, lockdown, or kernel configuration; concurrency and process ordering can make trace matching fragile. Test signals: harness uses exact diff matching; generated `.gen.test` scripts and `gen_tests.am` are build outputs.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/gen_tests.in -->
