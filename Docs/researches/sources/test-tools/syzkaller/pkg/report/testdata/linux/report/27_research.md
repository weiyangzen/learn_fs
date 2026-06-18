<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/27 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/27

## Purpose
This minimal lockdep fixture verifies corrupted handling for an incomplete circular-locking report. Expected title is `possible deadlock in flush_workqueue`, type `LOCKDEP`, and `CORRUPTED: Y`.

## Important APIs, Types, and Functions
The file uses `TITLE`, `TYPE`, and `CORRUPTED` headers, followed by the beginning of a 2.6.32 lockdep report. The only meaningful target frame is `flush_workqueue+0x0/0xb0`.

## Control Flow
The reporter identifies a possible circular locking dependency and an attempted lock site, but the report is truncated before a full dependency chain and backtrace. It must still infer the lockdep title while marking the result corrupted.

## State and Persistence Behavior
No runtime state exists. Persistent expected state is title, type, corruption flag, and a short raw partial log.

## Dependencies and Integration Points
It depends on lockdep report matching and corruption detection for incomplete reports.

## Risks and Edge Cases
Too-permissive parsing could mark the truncated report as clean, while too-strict parsing could fail to preserve the useful `flush_workqueue` title.

## Test Signals
Expected output is `possible deadlock in flush_workqueue`, type `LOCKDEP`, and `CORRUPTED: Y`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/27 -->
