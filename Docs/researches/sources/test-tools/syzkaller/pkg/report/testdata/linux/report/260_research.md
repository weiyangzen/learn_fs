<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/260 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/260

## Purpose
This fixture verifies general-protection-fault parsing for a 9p connection cancellation path. The expected title is `general protection fault in p9_conn_cancel`, alt `bad-access in p9_conn_cancel`, type `DoS`, and `PANICKED: Y`.

## Important APIs, Types, and Functions
The log includes KASAN configuration lines, `general protection fault: 0000`, register dump, call trace, and fatal panic. Parser paths include GPF matching, frame selection, bad-access alt generation, and panic detection. Key symbols include `perf_trace_lock`, `perf_trace_lock_acquire`, `find_held_lock`, `__lock_acquire`, `lock_release`, `p9_conn_cancel`, `p9_fd_cancelled`, `p9_poll_workfn`, `process_one_work`, and worker-thread frames.

## Control Flow
The first RIP is in tracing/lock instrumentation, but the call trace includes the 9p cancellation path. The reporter must step past instrumentation and lockdep helpers to title the report at `p9_conn_cancel`, then record the later fatal-exception panic.

## State and Persistence Behavior
The persistent contract is title, alt, type `DoS`, and panic flag over a 119-line raw log. No mutable state is present.

## Dependencies and Integration Points
It depends on Linux GPF oops patterns, stack-frame skip lists, KASAN/noise handling, panic detection, and syzkaller crash-type mapping.

## Risks and Edge Cases
Instrumentation frames are prominent and could be chosen incorrectly. The report also mixes workqueue context and lock tracing, which tests parser resilience against noisy helper stacks.

## Test Signals
Expected output centers on `p9_conn_cancel`, includes `bad-access in p9_conn_cancel`, maps to `DoS`, and marks `PANICKED: Y`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/260 -->
