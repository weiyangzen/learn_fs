# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/29

Purpose: OpenBSD truncated fault fixture. Expected title is `uvm_fault`; expected `CORRUPTED: Y`.

Important parser APIs and patterns: targets the `uvm_fault(` oops group. The fallback format has `title: compile("uvm_fault\\(")`, `fmt: "uvm_fault"`, and `corrupted: true` for incomplete fault reports.

Control flow: the file contains a carriage-return-prefixed `uvm_fault(...) -> e` line and a `kernel: page fault trap, code=0` line, but no `Stopped at` function or `end trace frame`. The parser should still detect a crash while marking the report corrupted.

State and persistence: static corrupted-log fixture. It captures only the faulting map address and virtual address, intentionally lacking stack or DDB state.

Dependencies and integration: validates OpenBSD CR/LF handling noted in `Reporter.ParseFrom` and the corrupted-report path in `openbsdOopses`.

Risks: if fallback matching is removed, truncated kernel faults are missed. If corruption is not marked, downstream triage may treat a low-information report as complete.

Test signals: exact title `uvm_fault`; `CORRUPTED: Y`; no frame should be required.
