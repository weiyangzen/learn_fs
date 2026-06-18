# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/28

Purpose: Negative OpenBSD fixture for a non-crash `uvm_fault` substring. The file has no expected `TITLE`, so the reporter should not produce a crash report.

Important parser APIs and patterns: `openbsdOopses` recognizes `uvm_fault(` and `kernel: page fault trap` patterns, but this line is `vmx_mprotect_ept: uvm_fault returns 14, GPA=...`. It should not match the `uvm_fault\\(` start condition nor the `kernel:` fault trap title formats.

Control flow: there is no DDB entry, panic, stack, or stopped-at frame. It is a single informational line from VMX/EPT code mentioning a fault return.

State and persistence: static no-crash test input. It preserves a guest physical address as a dynamic value that should be ignored because no report is generated.

Dependencies and integration: integrates with `ContainsCrash` and `Parse` negative tests for OpenBSD. It prevents broad substring matching from treating informational fault messages as kernel crashes.

Risks: changing crash detection from strict oops headers to loose substring search could create false positives and noisy syzkaller reports.

Test signals: expected behavior is no report. Any non-nil parse result for this file is a regression.
