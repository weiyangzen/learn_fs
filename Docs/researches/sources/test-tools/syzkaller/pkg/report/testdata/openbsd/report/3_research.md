# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/3

Purpose: Minimal OpenBSD page-fault fixture with a stopped function. Expected title is `uvm_fault: vn_writechk`.

Important parser APIs and patterns: handled by the `kernel:` oops group, specifically `kernel: page fault trap, code=0.*\\nStopped at[ ]+([^\\+]+)` formatted as `uvm_fault: %[1]v`.

Control flow: the log contains a `login:` prompt, a carriage-return-prefixed `kernel: page fault trap`, and `Stopped at vn_writechk+0x13`. There is no full DDB trace, so parser success depends on the `kernel:` plus `Stopped at` title path.

State and persistence: static minimal fixture with no persistent runtime state. It preserves the exact terminal prompt and CR-prefixed lines that OpenBSD console output can emit.

Dependencies and integration: tests the OpenBSD reporter’s ability to extract a useful faulting function without a complete panic report or `uvm_fault(` line.

Risks: line-ending normalization and prefix stripping are critical. A parser that expects `uvm_fault(` or a full trace would miss this crash.

Test signals: exact title `uvm_fault: vn_writechk`; the only required frame signal is the `Stopped at vn_writechk+0x13` line.
