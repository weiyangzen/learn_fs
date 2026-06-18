# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/30

Purpose: Smallest OpenBSD corrupted `uvm_fault` fixture. Expected title is `uvm_fault`; expected `CORRUPTED: Y`.

Important parser APIs and patterns: exercises the corrupted fallback in the `uvm_fault(` oops group: `title: compile("uvm_fault\\(")`, `fmt: "uvm_fault"`, `corrupted: true`.

Control flow: after metadata, the raw body contains only one carriage-return-prefixed `uvm_fault(...) -> e` line. There is no `kernel:` line, no `Stopped at`, no trace, and no DDB prompt.

State and persistence: static truncation sample. The only kernel state is the fault map/address tuple; it is not enough to identify a faulting function.

Dependencies and integration: validates that OpenBSD crash detection can still classify severely truncated output as a corrupted crash report. This protects against VM or serial-console loss around a real fault.

Risks: broadening negative filters could accidentally suppress this because it lacks full context. Conversely, the fallback must remain specific to `uvm_fault(` to avoid false positives like report/28.

Test signals: exact title `uvm_fault`; corrupted flag set; no stack requirement.
