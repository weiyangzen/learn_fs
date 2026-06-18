# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/9

Purpose: OpenBSD kernel assertion fixture in UVM fault unwiring. Expected title is `assert "next != NULL && next->start <= entry->end" failed in uvm_fault.c`.

Important parser APIs and patterns: uses the assertion regex in `openbsdOopses`, extracting the assertion expression and source basename from `panic: kernel diagnostic assertion ... file ".../uvm_fault.c"`.

Control flow: panic occurs in `__assert`, then `uvm_fault_unwire_locked`, `uvm_fault_unwire`, `physio`, `spec_read`, `VOP_READ`, `vn_read`, `dofilereadv`, `sys_read`, syscall, and `Xsyscall`. The log includes line wrapping inside `physio` and `dofilereadv` argument lists.

State and persistence: static fixture preserving virtual address range arguments and process context. The assertion expression is stable semantic state; addresses and syscall arguments are noisy.

Dependencies and integration: validates OpenBSD assertion parsing for UVM paths and stack parsing across wrapped lines.

Risks: if the regex is too greedy or path trimming fails, title could include manager-specific prefixes or line numbers. Wrapped frames can confuse stack extraction.

Test signals: exact assertion title; stack includes `uvm_fault_unwire_locked`.
