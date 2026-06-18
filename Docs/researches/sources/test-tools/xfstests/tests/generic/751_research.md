# sources/test-tools/xfstests/tests/generic/751


Purpose: Stresses page-cache truncation, large folio splitting, and writeback by running buffered fio writes while continuously forcing huge-page split operations.


Important APIs, helpers, and commands: Defines `proc_vmstat`; uses `_require_split_huge_pages_knob`, `_split_huge_pages_all`, `_require_fio`, `FIO_PROG`, and vmstat counters `thp_split_page`/`thp_split_page_failed`.
 Local helper functions detected in the file include `_cleanup`, `proc_vmstat`.
 It imports `./common/preamble`.
 Capability gates include `_require_fio`, `_require_scratch`, `_require_split_huge_pages_knob`, `_require_test`.
 Regression annotations include `_fixed_by_git_commit kernel 2a0774c2886d \`.



Control flow, state, dependencies, risks, and test signals: It writes a fio config for many 4MiB buffered writers, mounts scratch, starts a runfile-controlled background split loop, records split counters, runs fio time-based writes, stops the loop, records counter deltas, and tolerates ENOSPC. State includes fio temp files, scratch files, huge-page split counters, and the split-loop PID. Dependencies are fio, THP split controls, buffered IO, and scratch capacity. Risks are intentionally aggressive system-wide split pressure, ENOSPC interpretation, and cleanup of background work. Signals are fio non-ENOSPC failure or kernel/writeback crash. Source size is 167 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.
