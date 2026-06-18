<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/354 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/354

## Purpose
This Trusty fixture covers a reflist assertion. The expected title is `trusty: ASSERT FAILED: list_in_list(&ref->ref_node)`, type `DoS`, panicked.

## Important APIs, Types, And Functions
The root line is `DEBUG ASSERT FAILED at (trusty/kernel/include/shared/lk/reflist.h:63): list_in_list(&ref->ref_node)`, followed by Trusty halt/crash markers, Linux `trusty_std_call32` warning, and arm64 workqueue stack in `nop_work_func`.

## Control Flow
The reporter prioritizes the Trusty panic/assertion text over the Linux warning wrapper. It then records panic-on-warn from the Linux kernel panic line.

## State And Persistence
The checked-in state is expected title/type/panic metadata and raw arm64 console output. Runtime state includes Trusty secure-world halt reason and Linux workqueue notification.

## Dependencies And Integration Points
It integrates with Trusty pattern matching, assertion-text extraction, arm64 stack parsing, and generic panic handling.

## Risks
If the parser strips too much Trusty text or selects `trusty_std_call32`, deduplication loses the secure-world assertion identity.

## Test Signals
Stable parsing returns the reflist assertion title exactly and marks `PANICKED: Y`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/354 -->
